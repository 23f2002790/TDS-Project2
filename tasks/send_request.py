from langchain_core.tools import tool
import requests
import json
from typing import Any, Dict, Optional


@tool
def post_request(url: str, payload: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> Any:
    """
    Submit the quiz answer to the URL provided by the task page.

    - Must be JSON only.
    - Waits for response so the agent knows what to do next.
    - Handles IITM quiz timers & next URL chaining rules.
    """

    headers = headers or {"Content-Type": "application/json"}

    print("\n📨 Submitting Answer:")
    print(json.dumps(payload, indent=4))
    print("➡ Endpoint:", url)

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()

        # Attempt to interpret response as JSON
        try:
            data = response.json()
        except ValueError:
            print("⚠️ Server didn't return JSON. Raw response kept.")
            return response.text

        # IITM quiz logic:
        # If wrong → server hides correct answer + sometimes hides URL
        delay = max(0, float(data.get("delay", 0) or 0))
        is_correct = data.get("correct")

        # Still time left → retry allowed → mask the next URL if wrong
        if not is_correct and delay < 180:
            data.pop("url", None)

        # Time exceeded → only URL allowed
        if delay >= 180:
            data = {"url": data.get("url")}

        print("📬 Server Response:")
        print(json.dumps(data, indent=4), '\n')

        return data

    except requests.HTTPError as e:
        # Extract server’s JSON error details if present
        err = e.response.text
        print("❌ HTTP Error:", err)
        return {"error": err}

    except Exception as e:
        print("❌ Unexpected Failure:", str(e))
        return {"error": str(e)}
