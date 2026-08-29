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

INTENT_MODEL = "gemini-flash-lite-latest"#"gemini-flash-latest" "gemini-3.6-flash" or 

MAX_WAIT_SEC=20

SYSTEM_PROMPT = """You are an intent classifier for a communication coaching agent.

First explain your reasoning, then classify into exactly one of:
Email Writing, Interview Practice, Grammar Correction, Tone Improvement,
Public Speaking, Conflict Resolution, Customer Communication, unclear.

Confidence level (use these, don't guess):
- high: message clearly and uniquely matches one intent, unambiguous keywords
- medium: matches one intent but is generic or could overlap another
- low: vague, multiple intents plausible, or not enough info

Known collisions - use these rules when words overlap across categories:
- "weakness", "strength", "practice", "practice for" + any reference to answering
  or being asked something -> Interview Practice, NOT Conflict Resolution or Public Speaking.
- "nervous", "presentation" -> Public Speaking. "nervous" alone about an interview -> Interview Practice.
- A request to write/draft something to a specific person -> Email Writing.
  A request to write/respond to a customer/client specifically -> Customer Communication.
- If the message asks to write/draft an "email" as the main request, classify as
  Email Writing even when the recipient is a client or customer - UNLESS the message
  centers on a customer-service issue (complaint, refund, angry customer, support
  ticket), in which case use Customer Communication instead.
- If the user explicitly requests to practice an interview question, prioritize Interview Practice.
- If the message is simply drafting/chasing correspondence with a client (following
  up, scheduling, general messages) -> Email Writing.
  If the message concerns a service issue, refund, complaint, or a change to
  pricing/policy/account terms affecting the client -> Customer Communication,
  even if phrased as "draft a message" or "write an email."

Examples:
"Can you check this sentence for errors?" -> Grammar Correction, confidence_level high
"Can you help me draft a message to my landlord?" -> Email Writing, confidence_level high
"I need to sound less aggressive in this message" -> Tone Improvement, confidence_level high
"Help me write to a client about a delayed shipment" -> Customer Communication, confidence_level high
"My coworker keeps taking credit for my work" -> Conflict Resolution, confidence_level high
"Can you give me a mock interview question?" -> Interview Practice, confidence_level high
"Help me practice answering 'What's your biggest weakness?'" -> Interview Practice, confidence_level high
"Write a follow-up email to a client who hasn't responded in two weeks" -> Email Writing, confidence_level high
"I want to talk to my manager about something that's been bothering me" -> Conflict Resolution, confidence_level medium
"I don't really know how to say this..." -> unclear, confidence_level low
"Draft a message to a client explaining a price increase" -> Customer Communication, confidence_level high
"""
INTENT_KEYWORDS = {
    "Email Writing": ["email", "write to", "message to", "draft"],
    "Interview Practice": ["interview", "behavioral question", "mock interview", "job interview"],
    "Grammar Correction": ["check this", "grammar", "correct", "fix this sentence"],
    "Tone Improvement": ["tone", "sound more", "come across", "less aggressive", "more professional"],
    "Public Speaking": ["speech", "presentation", "speaking", "public speaking", "public talk"],
    "Conflict Resolution": ["conflict", "disagreement", "argument", "coworker", "higher authority", "subordinate"],
    "Customer Communication": ["customer", "client", "support ticket"],
    "unclear": [],
}


def sanity_check(intent: str, message: str) -> bool:
    keywords = INTENT_KEYWORDS.get(intent, [])
    if not keywords:
        return True
    return any(k.lower() in message.lower() for k in keywords)


def _single_classify(message: str, max_retries: int = 4) -> IntentResult:
    last_error = None
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=INTENT_MODEL,
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
                rqst_wait = float(match.group(1)) + 2 if match else 60
                wait=min(rqst_wait,MAX_WAIT_SEC)
                print(f"  [rate limited] waiting {wait:.0f}s before retry {attempt+1}/{max_retries}...")
                time.sleep(wait)
                last_error = e
                continue
            raise

        except ServerError as e:
            wait = min(2 ** attempt,MAX_WAIT_SEC)
            print(f"  [server busy] retry {attempt+1}/{max_retries}, waiting {wait}s...")
            time.sleep(wait)
            last_error = e

    raise last_error


def classify_intent(message: str) -> IntentResult:
    result = _single_classify(message)

    if result.confidence_level == "high":
        return result

    if result.confidence_level == "medium":
        extra = [_single_classify(message) for _ in range(2)]
        votes = [result.intent.value] + [r.intent.value for r in extra]
        top_intent, count = Counter(votes).most_common(1)[0]

        if count < 2:
            return IntentResult(
                reasoning=f"No majority across 3 samples: {votes}",
                intent=Intent.UNCLEAR,
                confidence_level="low",
            )
        if top_intent != result.intent.value:
            result = next(r for r in [result] + extra if r.intent.value == top_intent)

    if not sanity_check(result.intent.value, message):
        return IntentResult(
            reasoning=f"Model chose {result.intent.value} but no matching keywords found; overriding to unclear.",
            intent=Intent.UNCLEAR,
            confidence_level="low",
        )

    return result
