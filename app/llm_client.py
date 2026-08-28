import os
import re
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import ServerError, ClientError

load_dotenv()
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])


def call_gemini(prompt: str, model: str = "gemini-flash-lite-latest", max_retries: int = 4):
    last_error = None
    for attempt in range(max_retries):
        try:
            return client.models.generate_content(model=model, contents=prompt)

        except ClientError as e:
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                match = re.search(r"retry in (\d+\.?\d*)s", str(e))
                wait = float(match.group(1)) + 2 if match else 60
                print(f"  [rate limited] waiting {wait:.0f}s before retry {attempt+1}/{max_retries}...")
                time.sleep(wait)
                last_error = e
                continue
            raise

        except ServerError as e:
            wait = 2 ** attempt
            print(f"  [server busy] retry {attempt+1}/{max_retries}, waiting {wait}s...")
            time.sleep(wait)
            last_error = e

    raise last_error
