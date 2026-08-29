from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google.genai.errors import ServerError, ClientError
from app.planner import classify_intent
from app.tools.router import TOOL_REGISTRY, handle_unclear
from app.schemas import CoachResponse, Intent

app = FastAPI(title="Agentic Communication Coach")


class UserMessageRequest(BaseModel):
    message: str


@app.get("/")
def root():
    return {"message": "Welcome to Agentic Communication Coach"}


@app.post("/coach/chat", response_model=CoachResponse)
def chat(payload: UserMessageRequest):
    user_text = payload.message.strip()
    if not user_text:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    try:
        intent_result = classify_intent(user_text)
        tool_handler = TOOL_REGISTRY.get(intent_result.intent, handle_unclear)
        return tool_handler(user_text)

    except (ClientError, ServerError):
        return CoachResponse(
            response="I'm getting a lot of requests right now. Please try again in a moment.",
            intent=Intent.UNCLEAR,
            clarify_pending=False,
            awaiting_followup=False,
        )
