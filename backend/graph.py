from langchain_deepseek import ChatDeepSeek
from langgraph.graph import StateGraph, END, START
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool
import numexpr
import sqlite3
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ── Tools Definition ─────────────────────────────────────
search = DuckDuckGoSearchRun()

@tool
def calculator(expression: str) -> str:
    """Calculate the result of a mathematical expression. 
    Input should be a mathematical expression like '2 + 2' or '25 * 4'."""
    try:
        # Using numexpr for safe and fast evaluation
        result = numexpr.evaluate(expression).item()
        return str(result)
    except Exception as e:
        return f"Error evaluating expression: {str(e)}"

tools = [search, calculator]
tool_node = ToolNode(tools)

# ── State ────────────────────────────────────────────────
class chatstate(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# ── LLM Node ─────────────────────────────────────────────
def chat_llm(state: chatstate, config: RunnableConfig) -> chatstate:
    llm = ChatDeepSeek(
        model="deepseek-chat",
        api_key=os.environ.get("DEEPSEEK_API_KEY"),
        temperature=config.get("configurable", {}).get("temperature", 0.7),
        max_tokens=config.get("configurable", {}).get("max_tokens", 1024),
    ).bind_tools(tools)
    
    # Pass config to llm.invoke to propagate metadata for LangSmith
    response = llm.invoke(state["messages"], config=config)
    return {"messages": [response]}

# ── Graph Assembly ────────────────────────────────────────
conn = sqlite3.connect("chatbot.db", check_same_thread=False)
memory = SqliteSaver(conn)

builder = StateGraph(chatstate)
builder.add_node("chat_llm", chat_llm)
builder.add_node("tools", tool_node)

builder.set_entry_point("chat_llm")

# Add conditional edges to handle tool calling
builder.add_conditional_edges(
    "chat_llm",
    tools_condition,
)

# Tools always return to the LLM
builder.add_edge("tools", "chat_llm")

graph = builder.compile(checkpointer=memory)

# ── Public Function ───────────────────────────────────────
def run_graph(
    message: str,
    thread_id: str,
    temperature: float = 0.7,
    max_tokens: int = 1024,
):
    config = {
        "configurable": {
            "thread_id": thread_id,
            "temperature": temperature,
            "max_tokens": max_tokens,
        },
        "metadata": {
            "thread_id": thread_id,
            "session_id": thread_id
        }
    }
    
    # We use multiple stream modes to get both message tokens and node updates
    for mode, data in graph.stream(
        {"messages": [HumanMessage(content=message)]},
        config=config,
        stream_mode=["messages", "updates"],
    ):
        if mode == "messages":
            msg, metadata = data
            if isinstance(msg, AIMessage) and msg.content:
                yield {"type": "text", "content": msg.content}
        elif mode == "updates":
            # If the 'tools' node is in the update, it means a tool was just called
            if "tools" in data:
                yield {"type": "tool", "status": "executing"}
            # If 'chat_llm' is in the update, we can check for tool calls
            elif "chat_llm" in data:
                msg = data["chat_llm"]["messages"][-1]
                if msg.tool_calls:
                    tool_names = [tc["name"] for tc in msg.tool_calls]
                    yield {"type": "tool_call", "names": tool_names}

def get_chat_history(thread_id: str):
    """Retrieve existing message history for a specific thread."""
    config = {
        "configurable": {"thread_id": thread_id},
        "metadata": {"thread_id": thread_id, "session_id": thread_id}
    }
    state = graph.get_state(config)
    if state.values:
        return state.values.get("messages", [])
    return []

def get_all_threads():
    """List all unique thread IDs stored in the SQLite database."""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT thread_id FROM checkpoints")
        return [row[0] for row in cursor.fetchall()]
    except sqlite3.OperationalError:
        return []

if __name__ == "__main__":
    # Test with a search query
    for token in run_graph(
        "Who is the current Prime Minister of Pakistan and what is 25 * 4?",
        "thread_test"
    ):
        print(token, end="", flush=True)
