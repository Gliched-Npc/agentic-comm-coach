from pydantic import BaseModel
from typing import Optional, List, Literal
from enum import Enum


class Intent(str, Enum):
    EMAIL_WRITING = "Email Writing"
    INTERVIEW_PRACTICE = "Interview Practice"
    GRAMMAR_CORRECTION = "Grammar Correction"
    TONE_IMPROVEMENT = "Tone Improvement"
    PUBLIC_SPEAKING = "Public Speaking"
    CONFLICT_RESOLUTION = "Conflict Resolution"
    CUSTOMER_COMMUNICATION = "Customer Communication"
    UNCLEAR = "unclear"


class IntentResult(BaseModel):
    reasoning: str
    intent: Intent
    confidence_level: Literal["low", "medium", "high"]


class PlanStep(BaseModel):
    reasoning: str
    tool: str
    input: str
    step: int


class Plan(BaseModel):
    plan: List[PlanStep]


class ScoreBreakdown(BaseModel):
    clarity: Optional[int] = None
    structure: Optional[int] = None
    specificity: Optional[int] = None
    tone: Optional[int] = None
    grammar: Optional[int] = None
    conciseness: Optional[int] = None


class CoachResponse(BaseModel):
    response: str
    intent: Intent
    score: Optional[ScoreBreakdown] = None
    clarify_pending: bool = False
    awaiting_followup: bool = False


class ChatTurn(BaseModel):
    role: str
    content: str
    intent: Optional[Intent] = None
    