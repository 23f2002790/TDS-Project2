# LLM Quiz Solver – Autonomous TDS Evaluation Agent

This project is part of the IITM BS **Tools in Data Science** course.  
It implements an **autonomous agent** that solves multi-step evaluation quizzes by:

- Scraping and analyzing webpages
- Downloading and processing data files
- Executing generated Python code
- Submitting answers to provided endpoints
- Navigating through linked quiz pages until completion

Evaluation is conducted using the TDS quiz server hosted at:  
https://tds-llm-analysis.s-anand.net  
(All rights and credits for the evaluation system belong to IITM & TDS Course Team.)

The system is powered by:
- **LangGraph (Stateful Agent Orchestration)**
- **Google Gemini 2.5 Flash API**
- **FastAPI backend**
- **Playwright for dynamic web rendering**

---

## 1️⃣ Architecture Overview

Client → FastAPI Server (/solve) → Autonomous LangGraph Agent
│
▼
Web Scraping / File Download / Code Execution
│
▼
Quiz Server Evaluation

yaml
Copy code

Agent Behavior:
- Read quiz instructions from each URL
- Decide correct tool execution path
- Submit results and detect next quiz link
- Continue until server response contains **no URL**, then end chain

---

## 2️⃣ Key Features

- Fully autonomous multi-page quiz solving
- Handles scraping, parsing, PDFs/CSVs, JSON APIs
- Executes generated Python safely in isolation
- Smart request routing with time validation
- Rate-limited to comply with TDS quiz quotas
- Background processing to avoid HTTP timeout
- Containerized – deployable to HuggingFace Spaces

---

## 3️⃣ Project Structure

LLM-Quiz-Solver/
│
├── main.py # FastAPI service (entrypoint)
├── agent.py # LangGraph state machine
├── tasks/ # Tooling layer for quiz interaction
│ ├── web_scraper.py # Playwright-based dynamic HTML fetch
│ ├── download_file.py # Save files locally for analysis
│ ├── send_request.py # Submit answers to quiz endpoints
│ ├── run_code.py # Execute code with uv subprocess
│ └── add_dependencies.py # Install missing python packages dynamically
│
├── test.py # Test suite for environment and agent flow
├── requirements.txt # Dependencies
├── Dockerfile # HuggingFace/Container deployment config
└── README.md

r
Copy code

### Component Roles

| Component | Responsibility |
|----------|----------------|
| `main.py` | Receives POST request, launches agent in background |
| `agent.py` | Core state machine: planning, routing, recursion |
| `tasks/get_rendered_html` | Browser-based dynamic scraping |
| `tasks/post_request` | Sends quiz answer submissions |
| `tasks/run_code` | Runs generated Python securely |
| `tasks/download_file` | Fetches datasets & media |
| `tasks/add_dependencies` | Auto-installs missing modules |
| `test.py` | Verification of all tool types (end-to-end sanity check) |

---

## 4️⃣ Installation Guide

### Requirements

- Python 3.10+
- Windows/Linux/Mac
- Playwright Chromium

### Setup Commands

```bash
git clone <repo-url>
cd LLM-Quiz-Solver

python -m venv venv
source venv/bin/activate   # mac/linux
venv\Scripts\activate      # windows

pip install -r requirements.txt
playwright install chromium
5️⃣ Environment Variables
Create .env file:

env
Copy code
EMAIL=<your IITM registered email>
SECRET=<secret from quiz page>
GOOGLE_API_KEY=<Gemini API key>
6️⃣ API Endpoints
Endpoint	Method	Description
/solve	POST	Start autonomous quiz solving
/healthz	GET	Service uptime check

Example Request
bash
Copy code
curl -X POST http://localhost:7860/solve \
-H "Content-Type: application/json" \
-d '{
  "url": "https://tds-llm-analysis.s-anand.net/demo",
  "secret": "<your secret>"
}'
7️⃣ Run Locally
bash
Copy code
python main.py
Server will run at:

arduino
Copy code
http://localhost:7860
8️⃣ Docker Deployment
Build image:

bash
Copy code
docker build -t llm-agent .
Run container:

bash
Copy code
docker run -p 7860:7860 \
-e EMAIL="..." \
-e SECRET="..." \
-e GOOGLE_API_KEY="..." \
llm-agent
9️⃣ HuggingFace Deployment
Create a Space → Select Docker runtime

Upload entire repository

Add secrets in Space settings:

EMAIL

SECRET

GOOGLE_API_KEY

Deploy automatically

The app will run at:

php-template
Copy code
https://<username>-<space>.hf.space/solve
🔟 Key Design Decisions
Decision	Benefit
State machine via LangGraph	Repeatable execution across multiple quiz hops
Browser automation	Supports JavaScript-heavy evaluation pages
Background tasks	Avoids blocking /solve response
Rate limiting	Prevents evaluation lockouts
Error-aware answer submission	Safe retries within allowed limits
Dynamic package installation	More task types supported automatically

1️⃣1️⃣ Testing the System
Run this:

bash
Copy code
python test.py
Test	Purpose
Test 1 — Simple fetch	Validate GET/POST parsing & secret
Test 2 — Dynamic scraping	Ensure Playwright runtime is working
Test 3 — File download	Validate dependencies & local saves
Test 4 — Code execution path	Ensure runtime execution sandbox is functional
Test 5 — Multi-step flow simulation	Verify LangGraph routing & recurrence

If all tests pass → deployment ready.

1️⃣2️⃣ Acknowledgment & Credits
✔ Quiz evaluation server developed by IIT Madras – Tools in Data Science course team
✔ Used only for academic and educational purposes
✔ Authentication values (EMAIL, SECRET) are user-specific and confidential

License
This project is distributed under the MIT License.