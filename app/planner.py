import os
import re
import time
from collections import Counter
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import ServerError, ClientError
from app.schemas import IntentResult, Intent

load_dotenv()
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

SYSTEM_PROMPT = """You are an intent classifier for a communication coaching agent.

First explain your reasoning, then classify into exactly one of:
Email Writing, Interview Practice, Grammar Correction, Tone Improvement,
Public Speaking, Conflict Resolution, Customer Communication, unclear.

Confidence bands (use these, don't guess):
- 0.8-1.0: message clearly and uniquely matches one intent, unambiguous keywords
- 0.5-0.79: matches one intent but is generic or could overlap another
- below 0.5: vague, multiple intents plausible, or not enough info

Examples:
"Can you check this sentence for errors?" -> Grammar Correction, confidence 0.95
"Can you help me draft a message to my landlord?" -> Email Writing, confidence 0.9
"I need to sound less aggressive in this message" -> Tone Improvement, confidence 0.9
"Help me write to a client about a delayed shipment" -> Customer Communication, confidence 0.85
"I have a presentation next week and I'm nervous" -> Public Speaking, confidence 0.8
"My coworker keeps taking credit for my work" -> Conflict Resolution, confidence 0.85
"Can you give me a mock interview question?" -> Interview Practice, confidence 0.9
"I don't really know how to say this..." -> unclear, confidence 0.3
"""

INTENT_KEYWORDS = {
    "Email Writing": ["email", "write to", "message to", "draft"],
    "Interview Practice": ["interview", "behavioral question", "mock"],
    "Grammar Correction": ["check this", "grammar", "correct", "fix this sentence"],
    "Tone Improvement": ["tone", "sound more", "come across", "less aggressive", "more professional"],
    "Public Speaking": ["speech", "presentation", "speaking", "talk"],
    "Conflict Resolution": ["conflict", "disagreement", "argument", "coworker"],
    "Customer Communication": ["customer", "client", "support ticket"],
    "unclear": [],
}


def sanity_check(intent: str, message: str) -> bool:
    keywords = INTENT_KEYWORDS.get(intent, [])
    if not keywords:
        return True
    return any(k in message.lower() for k in keywords)


def _single_classify(message: str, max_retries: int = 4) -> IntentResult:
    last_error = None
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-flash-lite-latest",
                contents=f"{SYSTEM_PROMPT}\n\nUser message: {message}",
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=IntentResult,
                ),
            )
            return IntentResult.model_validate_json(response.text)

        except ClientError as e:
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                match = re.search(r"retry in (\d+\.?\d*)s", str(e))
                wait = float(match.group(1)) + 2 if match else 60
                print(f"  [rate limited] waiting {wait:.0f}s before retry {attempt+1}/{max_retries}...")
                time.sleep(wait)
                last_error = e
                continue
            raise  
        except ServerError as e:
            wait = 2 ** attempt
            print(f"  [server busy] retry {attempt+1}/{max_retries}, waiting {wait}s...")
            time.sleep(wait)
            last_error = e

    raise last_error


def classify_intent(message: str) -> IntentResult:
    result = _single_classify(message)

    if 0.5 <= result.confidence < 0.8:
        extra = [_single_classify(message) for _ in range(2)]
        votes = [result.intent.value] + [r.intent.value for r in extra]
        top_intent, count = Counter(votes).most_common(1)[0]

        if count < 2:
            return IntentResult(
                reasoning=f"No majority across 3 samples: {votes}",
                intent=Intent.UNCLEAR,
                confidence=0.3,
            )
        if top_intent != result.intent.value:
            result = next(r for r in [result] + extra if r.intent.value == top_intent)

    if not sanity_check(result.intent.value, message):
        return IntentResult(
            reasoning=f"Model chose {result.intent.value} but no matching keywords found; overriding to unclear.",
            intent=Intent.UNCLEAR,
            confidence=0.3,
        )

    return result
