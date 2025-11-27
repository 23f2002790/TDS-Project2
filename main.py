from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import uvicorn
import time
import os

from agent import run_agent

load_dotenv()

# Environment values used by IITM evaluation server
EMAIL = os.getenv("EMAIL")
SECRET = os.getenv("SECRET")

app = FastAPI()

# Allow access from anywhere (more useful during deployment)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Uptime tracking just to confirm container/server is alive
START_TIME = time.time()


@app.get("/healthz")
def health_check():
    """Ping test — IITM script checks this."""
    return {
        "status": "ok",
        "uptime": int(time.time() - START_TIME)
    }


@app.post("/solve")
async def solve_quiz(request: Request, background_tasks: BackgroundTasks):
    """
    Main endpoint:
    - Validate input JSON
    - Validate student secret
    - Trigger autonomous agent in background
    - Immediate return so server does not timeout
    """
    try:
        data = await request.json()
    except Exception:
        return JSONResponse(status_code=400, content={"error": "Invalid JSON"})

    url = data.get("url")
    secret = data.get("secret")

    if not url or not secret:
        return JSONResponse(status_code=400, content={"error": "Missing fields"})

    if secret != SECRET:
        return JSONResponse(status_code=403, content={"error": "Invalid secret"})

    print(f"✔ Request Authenticated — starting quiz: {url}")
    
    # Start agent async → important or IITM server times out
    background_tasks.add_task(run_agent, url)

    return JSONResponse(status_code=200, content={"status": "ok"})


if __name__ == "__main__":
    # Local development
    uvicorn.run(app, host="0.0.0.0", port=7860)
