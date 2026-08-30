from app.planner import classify_intent

TEST_MESSAGES = {
    "Email Writing": [
        "Can you help me write an email to my landlord about a leaking faucet?",
        "I need to draft a message to HR requesting time off.",
        "Write a follow-up email to a client who hasn't responded in two weeks.",
    ],
    "Interview Practice": [
        "Can you give me a mock interview question about teamwork?",
        "Help me practice answering 'What's your biggest weakness?'",
        "I have a job interview tomorrow, can we do a practice round?",
    ],
    "Grammar Correction": [
        "Check this: 'Me and him goes to the store yesterday.'",
        "Is this sentence correct: 'She don't like coffee.'",
        "Fix the grammar in: 'Their going to the park later.'",
    ],
    "Tone Improvement": [
        "Can you make this message sound less aggressive?",
        "I want this email to sound more professional.",
        "Does this come across as too casual for a client?",
    ],
    "Public Speaking": [
        "I have a presentation next week and I'm nervous.",
        "Help me structure a 5-minute speech about teamwork.",
        "How do I stop rambling when I give a talk?",
    ],
    "Conflict Resolution": [
        "My coworker keeps taking credit for my work, how do I address this?",
        "I had an argument with my manager, how should I follow up?",
        "How do I bring up a disagreement without sounding confrontational?",
    ],
    "Customer Communication": [
        "Help me write to a client about a delayed shipment.",
        "A customer is angry about a refund, how should I respond?",
        "Draft a message to a client explaining a price increase.",
    ],
    "unclear": [
        "I don't really know how to say this...",
        "Can you help me?",
        "So basically the thing is...",
    ],
}

correct = 0
total = 0
for expected, messages in TEST_MESSAGES.items():
    for msg in messages:
        result = classify_intent(msg)
        total += 1
        match = "PASS" if result.intent.value == expected else "FAIL"
        if match == "PASS":
            correct += 1
        print(f"{match} | expected={expected} got={result.intent.value} conf={result.confidence_level} | {msg}")

print(f"\n{correct}/{total} correct ({correct/total*100:.0f}%)")