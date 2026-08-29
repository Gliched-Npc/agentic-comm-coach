# app/tools/router.py
from typing import Callable, Dict
from app.schemas import Intent, CoachResponse
from app.tools.email_gen import generate_email
from app.tools.interview_coaching import interview_coaching
from app.tools.tone_analysis import tone_analysis

def handle_email_writing(message: str) -> CoachResponse:
    result = generate_email(message)
    return CoachResponse(
        response=result,
        intent=Intent.EMAIL_WRITING,
        clarify_pending=False,
        awaiting_followup=False
    )

def handle_interview_practice(message: str) -> CoachResponse:
    result = interview_coaching(message)
    return CoachResponse(
        response=result,
        intent=Intent.INTERVIEW_PRACTICE,
        clarify_pending=False,
        awaiting_followup=True
    )


def handle_tone_improvement(message: str) -> CoachResponse:
    result = tone_analysis(message)
    return CoachResponse(
        response=result,
        intent=Intent.TONE_IMPROVEMENT,
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
    Intent.INTERVIEW_PRACTICE: handle_interview_practice,
    Intent.TONE_IMPROVEMENT: handle_tone_improvement,
    Intent.UNCLEAR: handle_unclear,
}