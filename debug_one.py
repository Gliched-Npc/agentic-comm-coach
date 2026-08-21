from app.planner import classify_intent, _single_classify, sanity_check

msg = "Help me practice answering 'What's your biggest weakness?'"

print("=== Single raw classification (no voting, no override) ===")
raw = _single_classify(msg)
print(f"intent: {raw.intent.value}")
print(f"confidence: {raw.confidence}")
print(f"reasoning: {raw.reasoning}")
print(f"sanity_check passes: {sanity_check(raw.intent.value, msg)}")

print("\n=== Full pipeline (with voting + sanity check applied) ===")
result = classify_intent(msg)
print(f"intent: {result.intent.value}")
print(f"confidence: {result.confidence}")
print(f"reasoning: {result.reasoning}")