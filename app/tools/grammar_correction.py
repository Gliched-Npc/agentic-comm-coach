from app.llm_client import call_gemini, format_history_context

GRAMMAR_SYSTEM_PROMPT = """You are a grammar and writing correction assistant.

Given a piece of text, do the following:
1. Provide the corrected version, fixing grammar, spelling, punctuation, and syntax errors.
2. List the specific errors that were fixed and briefly explain each one (e.g. subject-verb
   agreement, wrong tense, pronoun case).

If the text has no errors, say so plainly rather than inventing changes to justify a response.

Keep it focused: the correction first, then a short list of what changed and why.
"""


def grammar_correction(message: str, history: list = None) -> str:
    history_context = format_history_context(history)
    prompt = f"{GRAMMAR_SYSTEM_PROMPT}{history_context}\n\nUser text: {message}"
    response = call_gemini(prompt)
    return response.text