# app/tools/router.py
from typing import Callable, Dict
from app.schemas import Intent, CoachResponse
from app.tools.email_gen import generate_email
from app.tools.interview_coaching import interview_coaching
from app.tools.tone_analysis import tone_analysis
from app.tools.conversation_improvement import conversation_improvement


def handle_email_writing(message: str,intent:Intent) -> CoachResponse:
    result = generate_email(message)
    return CoachResponse(
        response=result,
        intent=intent,
        clarify_pending=False,
        awaiting_followup=False
    )

def handle_interview_practice(message: str,intent:Intent) -> CoachResponse:
    result = interview_coaching(message)
    return CoachResponse(
        response=result,
        intent=intent,
        clarify_pending=False,
        awaiting_followup=True
    )


def handle_tone_improvement(message: str,intent:Intent) -> CoachResponse:
    result = tone_analysis(message)
    return CoachResponse(
        response=result,
        intent=intent,
        clarify_pending=False,
        awaiting_followup=False
    )


def handle_conversation_improvement(message: str,intent:Intent) -> CoachResponse:
    result = conversation_improvement(message)
    return CoachResponse(
        response=result,
        intent=intent,
        clarify_pending=False,
        awaiting_followup=False
    )

def handle_unclear(message: str,intent:Intent) -> CoachResponse:
    return CoachResponse(
        response=(
        "I'm not quite sure what kind of communication help you're looking for.\n\n"
        "Could you tell me a bit more? For example:\n"
        "- Are you trying to write something (an email, a message)?\n"
        "- Are you preparing for a conversation (an interview, a difficult talk)?\n"
        "- Do you want feedback on how something comes across?"
        ),
        intent=intent,
        clarify_pending=True,
        awaiting_followup=False
    )

TOOL_REGISTRY: Dict[Intent, Callable[[str,Intent], CoachResponse]] = {
    Intent.EMAIL_WRITING: handle_email_writing,
    Intent.INTERVIEW_PRACTICE: handle_interview_practice,
    Intent.TONE_IMPROVEMENT: handle_tone_improvement,
    Intent.PUBLIC_SPEAKING: handle_conversation_improvement,
    Intent.CONFLICT_RESOLUTION: handle_conversation_improvement,
    Intent.CUSTOMER_COMMUNICATION: handle_conversation_improvement,
    Intent.UNCLEAR: handle_unclear,
}