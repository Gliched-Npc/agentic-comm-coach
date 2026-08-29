# app/tools/router.py
from typing import Callable, Dict
from app.schemas import Intent, CoachResponse
from app.tools.email_gen import generate_email

def handle_email_writing(message: str) -> CoachResponse:
    draft = generate_email(message)
    return CoachResponse(
        response=draft,
        intent=Intent.EMAIL_WRITING,
        clarify_pending=False,
        awaiting_followup=False
    )

def handle_unclear(message: str) -> CoachResponse:
    return CoachResponse(
        response="I'm not quite sure how to help with that. Could you clarify if you want help drafting an email, preparing for an interview, fixing grammar, or adjusting tone?",
        intent=Intent.UNCLEAR,
        clarify_pending=True,
        awaiting_followup=False
    )

TOOL_REGISTRY: Dict[Intent, Callable[[str], CoachResponse]] = {
    Intent.EMAIL_WRITING: handle_email_writing,
    Intent.UNCLEAR: handle_unclear,
}