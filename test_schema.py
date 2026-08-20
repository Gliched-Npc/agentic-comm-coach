
from app.schemas import Intent, IntentResult, PlanStep, Plan, CoachResponse
from pydantic import ValidationError

def check(label, fn):
    try:
        fn()
        print(f"PASS: {label}")
    except AssertionError as e:
        print(f"FAIL: {label} -> {e}")

# 1. Valid data should construct cleanly
def test_valid_intent():
    r = IntentResult(reasoning="clear email request", intent="Email Writing", confidence=0.9)
    assert r.intent == Intent.EMAIL_WRITING

check("valid IntentResult constructs", test_valid_intent)

# 2. Invalid intent value should be REJECTED, not silently accepted
def test_invalid_intent_rejected():
    try:
        IntentResult(reasoning="x", intent="Not A Real Intent", confidence=0.5)
        assert False, "should have raised ValidationError but didn't"
    except ValidationError:
        pass  # this is the correct outcome

check("invalid intent value is rejected", test_invalid_intent_rejected)

# 3. Missing a required field should be REJECTED
def test_missing_field_rejected():
    try:
        IntentResult(intent="Email Writing", confidence=0.9)  # no 'reasoning'
        assert False, "should have raised ValidationError but didn't"
    except ValidationError:
        pass

check("missing required field is rejected", test_missing_field_rejected)

# 4. Parsing from a raw JSON string — this is what real Gemini output looks like
def test_json_parsing():
    raw = '{"reasoning": "user wants to practice interview", "intent": "Interview Practice", "confidence": 0.85}'
    parsed = IntentResult.model_validate_json(raw)
    assert parsed.intent == Intent.INTERVIEW_PRACTICE
    assert parsed.confidence == 0.85

check("parses from JSON string like Gemini would return", test_json_parsing)

# 5. Plan with multiple steps
def test_plan_multi_step():
    p = Plan(plan=[
        PlanStep(reasoning="ask question first", tool="interview_coaching", input="generate mock question", step=1),
        PlanStep(reasoning="wait for response", tool="await_user_response", input="", step=2),
    ])
    assert len(p.plan) == 2
    assert p.plan[0].step == 1

check("multi-step Plan constructs correctly", test_plan_multi_step)

# 6. CoachResponse — optional fields should default without you providing them
def test_coach_response_defaults():
    r = CoachResponse(response="here's your draft", intent="Email Writing")
    assert r.score is None
    assert r.clarify_pending is False
    assert r.awaiting_followup is False

check("CoachResponse optional fields default correctly", test_coach_response_defaults)

print("\nDone.")
