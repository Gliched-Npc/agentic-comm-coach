import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from app.llm_client import call_gemini

EMAIL_SYSTEM_PROMPT = """You are an executive communication coach specializing in workplace email strategy and drafting.

Determine whether the user needs an actionable email draft or advisory coaching:

1. MODE SELECTION:
   - DRAFTING (User asks to write/draft an email):
     * Generate a complete, ready-to-use email (Subject + Body).
     * Use bracketed placeholders like [Date], [Project Name] for missing specific details.
     * Follow with a brief 2-3 sentence coaching note explaining key structural or phrasing decisions.
   - COACHING / GUIDANCE (User asks "how should I ask...", "how to approach...", "tips for..."):
     * Do NOT generate a complete boilerplate email draft.
     * Provide concise, tactical guidance: strategic angle, key points to emphasize/avoid, and 1-2 adaptable phrasing examples.

2. TONE & REGISTER ADAPTATION:
   - FORMAL / UPWARD (Senior leadership, formal client escalations, leave applications):
     Respectful, deferential, accountable, and polished. Avoid overly casual idioms (e.g., use "Best regards," / "Dear [Name]"). Emphasize solutions, handover plans, and appreciation.
   - SEMI-FORMAL (Direct managers with good rapport, cross-functional peers, regular client updates):
     Professional, clear, warm, and approachable (e.g., "Hi [Name]", "Best,").
   - CASUAL / COLLABORATIVE (Close teammates, quick internal updates):
     Direct, friendly, and concise.

Deliver direct, high-impact responses without meta-introductions.
"""


def generate_email(message: str) -> str:
    prompt = f"{EMAIL_SYSTEM_PROMPT}\n\nUser request: {message}"
    response = call_gemini(prompt)
    return response.text


if __name__ == "__main__":
    print("=" * 60)
    print(" Agentic Communication Coach - Email Generation Tool")
    print("=" * 60)
    print("Type your email request below (or type 'exit' to quit).\n")

    while True:
        try:
            user_input = input("Enter request: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit", "q"):
                print("\nGoodbye!")
                break

            print("\n Generating email draft & coaching advice\n")
            result = generate_email(user_input)
            print("-" * 60)
            print(result)
            print("-" * 60 + "\n")
        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            break

