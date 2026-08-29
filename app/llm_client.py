import os
import re
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import ServerError, ClientError

load_dotenv()
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

MAX_WAIT_SEC=20
MODEL = "gemini-flash-lite-latest"#"gemini-flash-latest" "gemini-3.6-flash" or 

def call_gemini(prompt: str, model: str = MODEL, max_retries: int = 2):
    last_error = None
    for attempt in range(max_retries):
        try:
            return client.models.generate_content(model=model, contents=prompt)

        except ClientError as e:
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                match = re.search(r"retry in (\d+\.?\d*)s", str(e))
                requst_wait = float(match.group(1)) + 2 if match else 60
                wait=min(requst_wait,MAX_WAIT_SEC)
                print(f"  [rate limited] waiting {wait:.0f}s before retry {attempt+1}/{max_retries}...")
                time.sleep(wait)
                last_error = e
                continue
            raise

        except ServerError as e:
            wait = min(2 ** attempt,MAX_WAIT_SEC)
            print(f"  [server busy] retry {attempt+1}/{max_retries}, waiting {wait}s...")
            time.sleep(wait)
            last_error = e

    raise last_error
