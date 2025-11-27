import os
from typing import TypedDict, Annotated, List
from dotenv import load_dotenv

from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages
from langchain_core.rate_limiters import InMemoryRateLimiter
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chat_models import init_chat_model

# Tools for handling quiz steps
from tasks import (
    get_rendered_html,
    download_file,
    post_request,
    run_code,
    add_dependencies
)

# Load .env credentials
load_dotenv()
EMAIL = os.getenv("STUDENT_EMAIL")
SECRET = os.getenv("SECRET")

# Recursion limit to allow multi-step task solving
RECURSION_LIMIT = 10000


# Agent state maintains conversation history
class AgentState(TypedDict):
    messages: Annotated[List, add_messages]


# Available execution tools
TASK_TOOLS = [
    get_rendered_html,
    download_file,
    post_request,
    run_code,
    add_dependencies
]


# Gemini configuration with API rate limits
rate_limiter = InMemoryRateLimiter(
    requests_per_second=9 / 60,
    max_bucket_size=9
)

model = init_chat_model(
    model_provider="google_genai",
    model="gemini-2.5-flash",
    rate_limiter=rate_limiter
).bind_tools(TASK_TOOLS)


# System rules control agent behavior
SYSTEM_PROMPT = f"""
You are an autonomous agent designed to solve multi-step quiz tasks.

Instructions:
1. Load and analyze each quiz page carefully.
2. Follow exactly the instructions provided on the page.
3. Submit solutions only to the endpoint specified on that page.
4. Include only required fields in submissions.
5. When a server response provides a new URL, fetch it immediately.
6. Continue until no further URL is returned.
7. Only then reply with: END

Credentials to include when required:
- EMAIL = {EMAIL}
- SECRET = {SECRET}

Avoid hallucinating URLs, endpoints, fields, values, or formats.
Retry if incorrect while within allowed delay.
Do not terminate early under any circumstance.
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    MessagesPlaceholder("messages"),
])

pipeline = prompt | model


# LLM inference node
def llm_step(state: AgentState):
    response = pipeline.invoke({"messages": state["messages"]})
    return {"messages": state["messages"] + [response]}


# Routing logic between LLM and tools
def next_action(state: AgentState):
    last_msg = state["messages"][-1]

    # Tool call detection (works for AIMessage and dict)
    tool_calls = getattr(last_msg, "tool_calls", None)
    if tool_calls:
        return "tools"

    # Extract content (works for both AIMessage and dict types)
    content = getattr(last_msg, "content", None)
    if content is None and isinstance(last_msg, dict):
        content = last_msg.get("content")

    # Detect completion signal
    if isinstance(content, str) and content.strip() == "END":
        return END

    # Continue LLM reasoning by default
    return "agent"


# Build graph execution engine
graph = StateGraph(AgentState)
graph.add_node("agent", llm_step)
graph.add_node("tools", ToolNode(TASK_TOOLS))

graph.add_edge(START, "agent")
graph.add_edge("tools", "agent")
graph.add_conditional_edges("agent", next_action)

app = graph.compile()


# Entry point for FastAPI background task
def run_agent(quiz_url: str) -> None:
    """
    Starts solving a quiz chain beginning from the given URL.
    """
    app.invoke(
        {"messages": [{"role": "user", "content": quiz_url}]},
        config={"recursion_limit": RECURSION_LIMIT},
    )
    print("Quiz solving completed")
