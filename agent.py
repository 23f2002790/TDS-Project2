import os
from typing import TypedDict, Annotated, List
from dotenv import load_dotenv

from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages
from langchain_core.rate_limiters import InMemoryRateLimiter
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# Gemini LLM client
from langchain_google_genai import ChatGoogleGenerativeAI

# Tools from your tasks folder
from tasks import (
    get_rendered_html,
    download_file,
    post_request,
    run_code,
    add_dependencies,
)

# Load keys from HuggingFace secrets
load_dotenv()
EMAIL = os.getenv("STUDENT_EMAIL")
SECRET = os.getenv("SECRET")
GOOGLE_KEY = os.getenv("GOOGLE_API_KEY")

RECURSION_LIMIT = 10000


# Graph State Representation
class AgentState(TypedDict):
    messages: Annotated[List, add_messages]


# Tools allowed for execution
TASK_TOOLS = [
    get_rendered_html,
    download_file,
    post_request,
    run_code,
    add_dependencies,
]


# ⭐ Gemini Model Setup
model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    api_key=GOOGLE_KEY,
).bind_tools(TASK_TOOLS)


SYSTEM_PROMPT = f"""
You are an autonomous IITM quiz solver agent.
Rules:
1️⃣ Load the quiz URL received as USER input.
2️⃣ Use tools only when needed:
   - Fetch HTML: get_rendered_html
   - Download & inspect files: download_file
   - Execute python: run_code
   - Submit answers: post_request
   - Install missing libs if required: add_dependencies
3️⃣ Use EMAIL={EMAIL} and SECRET={SECRET} when submission requires them.
4️⃣ Continue solving until NO "url" is returned by quiz server.
5️⃣ Final message MUST be ONLY: END
6️⃣ Do NOT hallucinate URLs, fields, formats, or code output.
7️⃣ If server delays are present, RETRY while time remains.
Proceed carefully. Think step-by-step.
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    MessagesPlaceholder("messages"),
])

pipeline = prompt | model


# Node: LLM reasoning step
def llm_step(state: AgentState):
    response = pipeline.invoke({"messages": state["messages"]})
    return {"messages": state["messages"] + [response]}


# Routing logic: choose tools vs continue
def next_action(state: AgentState):
    last_msg = state["messages"][-1]

    if getattr(last_msg, "tool_calls", None):
        return "tools"

    content = getattr(last_msg, "content", None)
    if isinstance(content, str) and content.strip() == "END":
        return END

    return "agent"


# Build the Autonomous Agent Graph
graph = StateGraph(AgentState)
graph.add_node("agent", llm_step)
graph.add_node("tools", ToolNode(TASK_TOOLS))
graph.add_edge(START, "agent")
graph.add_edge("tools", "agent")
graph.add_conditional_edges("agent", next_action)

app = graph.compile()


# 🚀 Entry point triggered by FastAPI background task
def run_agent(quiz_url: str):
    print(f"\n🚀 Starting from: {quiz_url}\n")
    app.invoke(
        {"messages": [{"role": "user", "content": quiz_url}]},
        config={"recursion_limit": RECURSION_LIMIT},
    )
    print("\n🎯 Autonomy Complete — Task Sequence Finished\n")
