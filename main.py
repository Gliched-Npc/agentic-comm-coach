import uuid
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from google.genai.errors import ServerError, ClientError
from app.planner import classify_intent
from app.tools.router import TOOL_REGISTRY, handle_unclear
from app.tools.communication_scoring import score_communication
from app.memory import get_history, append_turn
from app.schemas import CoachResponse, Intent, ScoringResult, ChatTurn

app = FastAPI(title="Agentic Communication Coach")


class UserMessageRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class AnalyzeRequest(BaseModel):
    text: str


@app.get("/")
def root():
    return {"message": "Welcome to Agentic Communication Coach"}


@app.post("/coach/chat", response_model=CoachResponse)
def chat(payload: UserMessageRequest):
    user_text = payload.message.strip()
    if not user_text:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    session_id = payload.session_id or str(uuid.uuid4())

    try:
        history = get_history(session_id) if payload.session_id else []
        intent_result = classify_intent(user_text, history=history)
        tool_handler = TOOL_REGISTRY.get(intent_result.intent, handle_unclear)
        result = tool_handler(user_text, intent_result.intent, session_id, history)

        append_turn(session_id, "user", user_text, intent=intent_result.intent.value)
        append_turn(session_id, "assistant", result.response, intent=intent_result.intent.value)

        return result

    except (ClientError, ServerError):
        return CoachResponse(
            response="I'm getting a lot of requests right now. Please try again in a moment.",
            intent=Intent.UNCLEAR,
            session_id=session_id,
            clarify_pending=False,
            awaiting_followup=False,
        )


@app.get("/coach/history/{session_id}", response_model=List[ChatTurn])
def history(session_id: str):
    turns = get_history(session_id, limit=50)
    if not turns:
        raise HTTPException(status_code=404, detail="No history found for this session_id.")
    return turns


@app.post("/coach/analyze", response_model=ScoringResult)
def analyze(payload: AnalyzeRequest):
    text = payload.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text cannot be empty.")

    try:
        return score_communication(text)

    except (ClientError, ServerError):
        raise HTTPException(
            status_code=503,
            detail="I'm getting a lot of requests right now. Please try again in a moment."
        )
