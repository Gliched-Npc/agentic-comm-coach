from app.llm_client import call_gemini
from app.schemas import ScoringResult

SCORING_SYSTEM_PROMPT = """You are evaluating a piece of written communication (an email,
message, or response) for quality.

First write brief reasoning discussing strengths and weaknesses across each dimension.
For each dimension, quote or reference a SPECIFIC word or phrase from the text as
evidence - do not give a general impression without pointing to something concrete
in the text itself.

Then assign scores. Use the bands below - do not guess:

CLARITY (1-5): 1 = confusing, needs clarification. 3 = understandable with some effort.
5 = immediately clear, no ambiguity.

TONE (1-5): 1 = mismatched for the likely audience. 3 = acceptable but not well-calibrated.
5 = precisely calibrated to audience and situation.

GRAMMAR (1-5): 1 = errors impede understanding. 3 = minor errors, no impact on understanding.
5 = no errors.

CONCISENESS (1-5): 1 = padded, repetitive. 3 = reasonably concise, room to tighten.
5 = every sentence earns its place.

After scoring, give feedback: 2-3 sentences on the single most impactful change,
quoting the specific wording that should change.
"""


def score_communication(message: str) -> ScoringResult:
    prompt = f"{SCORING_SYSTEM_PROMPT}\n\nText to evaluate: {message}"
    response = call_gemini(prompt, response_schema=ScoringResult)
    return ScoringResult.model_validate_json(response.text)