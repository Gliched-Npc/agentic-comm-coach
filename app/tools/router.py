# app/tools/router.py
from typing import Callable, Dict, List
from app.schemas import Intent, CoachResponse,ChatTurn
from app.tools.email_gen import generate_email
from app.tools.interview_coaching import interview_coaching
from app.tools.tone_analysis import tone_analysis
from app.tools.conversation_improvement import conversation_improvement
from app.tools.grammar_correction import grammar_correction


def handle_email_writing(message: str,intent:Intent, session_id: str, history: List[ChatTurn] = None) -> CoachResponse:
    result = generate_email(message, history=history)
    return CoachResponse(
        response=result,
        intent=intent,
        session_id=session_id,
        clarify_pending=False,
        awaiting_followup=False
    )

def handle_interview_practice(message: str,intent:Intent, session_id: str, history: List[ChatTurn] = None) -> CoachResponse:
    result = interview_coaching(message, history=history)
    return CoachResponse(
        response=result,
        intent=intent,
        session_id=session_id,
        clarify_pending=False,
        awaiting_followup=True
    )


def handle_tone_improvement(message: str,intent:Intent, session_id: str, history: List[ChatTurn] = None) -> CoachResponse:
    result = tone_analysis(message, history=history)
    return CoachResponse(
        response=result,
        intent=intent,
        session_id=session_id,
        clarify_pending=False,
        awaiting_followup=False
    )


def handle_conversation_improvement(message: str,intent:Intent, session_id: str, history: List[ChatTurn] = None) -> CoachResponse:
    result = conversation_improvement(message, history=history)
    return CoachResponse(
        response=result,
        intent=intent,
        session_id=session_id,
        clarify_pending=False,
        awaiting_followup=False
    )

def handle_grammar_correction(message:str,intent:Intent, session_id: str, history: List[ChatTurn] = None) -> CoachResponse:
    result = grammar_correction(message, history=history)
    return CoachResponse(
        response=result,
        intent=intent,
        session_id=session_id,
        clarify_pending=False,
        awaiting_followup=False
    )

def handle_small_talk(message: str, intent: Intent, session_id: str, history: list = None) -> CoachResponse:
    lower = message.lower()
    if "thank" in lower:
        response = "You're welcome! Let me know if there's anything else you'd like help with."
    elif "bye" in lower or "goodbye" in lower:
        response = "Take care! Come back anytime you need help with communication."
    else:
        response = "Happy to help! Let me know what you'd like to work on."
    return CoachResponse(response=response, intent=intent, session_id=session_id, clarify_pending=False, awaiting_followup=False)

def handle_unclear(message: str,intent:Intent, session_id: str, history: List[ChatTurn] = None) -> CoachResponse:
    return CoachResponse(
        response=(
        "I'm not quite sure what kind of communication help you're looking for.\n\n"
        "Could you tell me a bit more? For example:\n"
        "- Are you trying to write something (an email, a message)?\n"
        "- Are you preparing for a conversation (an interview, a difficult talk)?\n"
        "- Do you want feedback on how something comes across?"
        ),
        intent=intent,
        session_id=session_id,
        clarify_pending=True,
        awaiting_followup=False
    )

TOOL_REGISTRY: Dict[Intent, Callable[[str,Intent,str], CoachResponse]] = {
    Intent.EMAIL_WRITING: handle_email_writing,
    Intent.INTERVIEW_PRACTICE: handle_interview_practice,
    Intent.TONE_IMPROVEMENT: handle_tone_improvement,
    Intent.PUBLIC_SPEAKING: handle_conversation_improvement,
    Intent.CONFLICT_RESOLUTION: handle_conversation_improvement,
    Intent.CUSTOMER_COMMUNICATION: handle_conversation_improvement,
    Intent.GRAMMAR_CORRECTION: handle_grammar_correction,
    Intent.SMALL_TALK: handle_small_talk,
    Intent.UNCLEAR: handle_unclear,
}