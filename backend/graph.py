from langchain_deepseek import ChatDeepSeek
from langgraph.graph import StateGraph, END, START
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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
    )
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

# ── Graph Assembly ────────────────────────────────────────
memory = MemorySaver()

builder = StateGraph(chatstate)
builder.add_node("chat_llm", chat_llm)
builder.set_entry_point("chat_llm")
builder.add_edge("chat_llm", END)

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
        }
    }
    for msg, metadata in graph.stream(
        {"messages": [HumanMessage(content=message)]},
        config=config,
        stream_mode="messages",
    ):
        if msg.content:
            yield msg.content

if __name__ == "__main__":
    for token in run_graph(
        "Hello, write 220 word blog on cricket",
        "thread_1"
    ):
        print(token, end="", flush=True)
