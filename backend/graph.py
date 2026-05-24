from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langgraph.graph import StateGraph, END, START
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool
import numexpr
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter# from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient

# ── Tools Definition ─────────────────────────────────────





# ── RAG Setup ─────────────────────────────────────────────
_retriever = None

def get_retriever():
    """Initializes the FAISS vector store once and caches the retriever."""
    global _retriever
    if _retriever is None:
        PDF_PATH = "how_to_talk_to_anyone.pdf"
        if not os.path.exists(PDF_PATH):
            print(f"Warning: {PDF_PATH} not found. RAG tool will be unavailable.")
            return None
        
        print(f"Initializing RAG retriever from {PDF_PATH}...")
        try:
            emb = OpenAIEmbeddings(model="text-embedding-3-large")
            loader = PyPDFLoader(PDF_PATH)
            docs = loader.load()
            splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
            splits = splitter.split_documents(docs)
            vs = FAISS.from_documents(splits, emb)
            _retriever = vs.as_retriever(search_type="similarity", search_kwargs={"k": 4})
        except Exception as e:
            print(f"Error initializing RAG: {e}")
            return None
    return _retriever

@tool
async def rag_node(query: str):
    """
    Search relevant context from the 'how_to_talk.pdf' document for the given query.
    Returns snippets from the document and their metadata.
    """
    retriever = get_retriever()
    if retriever is None:
        return {"error": "RAG retriever is not available (PDF missing or initialization failed)."}
        
    result = await retriever.ainvoke(query)
    return {
        "query": query,
        "context": [doc.page_content for doc in result],
        "metadata": [doc.metadata for doc in result]
    }






# 4) Prompt
    

    
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

# MCP Setup
MCP_SERVER_PATH = os.getenv("MCP_SERVER_PATH")
FASTMCP_EXE_PATH = os.getenv("FASTMCP_EXE_PATH")

mcp_server_config = {
    "gas_tracker": {
        "transport": "stdio",
        "command": FASTMCP_EXE_PATH,
        "args": ["run", MCP_SERVER_PATH]
    }
}

# Global client and tools list
mcp_client = None
mcp_tools = []

async def get_all_tools():
    global mcp_client, mcp_tools
    
    if mcp_client == "FAILED":
        return [search, calculator]

    mcp_path = os.getenv("MCP_SERVER_PATH")
    mcp_exe = os.getenv("FASTMCP_EXE_PATH")
    
    if not mcp_path or not mcp_exe:
        return [search, calculator,rag_node]

    if mcp_client is None:
        try:
            config = {
                "gas_tracker": {
                    "transport": "stdio",
                    "command": mcp_exe,
                    "args": ["run", mcp_path]
                }
            }
            mcp_client = MultiServerMCPClient(config)
            # MultiServerMCPClient version 0.1.0+ does not support __aenter__
            # It connects automatically on first use or via get_tools()
            mcp_tools = await asyncio.wait_for(mcp_client.get_tools(), timeout=30.0)
        except Exception as e:
            print(f"MCP Disabled: {e}")
            mcp_tools = []
            mcp_client = "FAILED" 
    
    return [search, calculator,rag_node] + (mcp_tools if isinstance(mcp_tools, list) else [])

# ── State ────────────────────────────────────────────────
class chatstate(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# ── LLM Node ─────────────────────────────────────────────
async def chat_llm(state: chatstate, config: RunnableConfig) -> chatstate:
    try:
        current_tools = await get_all_tools()
        
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        
        if current_tools:
            llm = llm.bind_tools(current_tools)
        
        # --- DeepSeek/Strict API Fix ---
        # Ensure history doesn't have "hanging" tool calls (AI messages with tool_calls
        # not followed by ToolMessages). This happens if a previous run was interrupted.
        messages = state["messages"]
        cleaned_messages = []
        for i, msg in enumerate(messages):
            if isinstance(msg, AIMessage) and msg.tool_calls:
                # Check if the very next message is a ToolMessage or if this is the last message
                # If a HumanMessage follows a tool call directly, it's invalid for DeepSeek.
                is_last = (i == len(messages) - 1)
                is_followed_by_human = (not is_last and isinstance(messages[i+1], HumanMessage))
                
                if is_followed_by_human:
                    # Convert to a plain AI message to satisfy API constraints
                    cleaned_messages.append(AIMessage(content=msg.content or "System: Tool calls were interrupted."))
                    continue
            cleaned_messages.append(msg)
        # --- End Fix ---

        response = await llm.ainvoke(cleaned_messages, config=config)
        return {"messages": [response]}
    except Exception as e:
        print(f"Error in chat_llm: {e}")
        return {"messages": [AIMessage(content=f"Error: {str(e)}")]}

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
import os

DB_URL = os.getenv("DATABASE_URL", "postgresql://chatbot:chatbot_password@postgres:5432/chatbot_db")

# ── Graph Factory ─────────────────────────────────────────
async def create_graph(checkpointer):
    """Factory function to create a fresh graph instance."""
    builder = StateGraph(chatstate)
    builder.add_node("chat_llm", chat_llm)
    
    async def tools_node_wrapper(state: chatstate, config: RunnableConfig):
        current_tools = await get_all_tools()
        node = ToolNode(current_tools)
        return await node.ainvoke(state, config=config)

    builder.add_node("tools", tools_node_wrapper)
    builder.set_entry_point("chat_llm")
    builder.add_conditional_edges("chat_llm", tools_condition)
    builder.add_edge("tools", "chat_llm")
    
    return builder.compile(checkpointer=checkpointer)

# ── Public Function ───────────────────────────────────────
async def run_graph(
    message: str,
    thread_id: str,
    temperature: float = 0.7,
    max_tokens: int = 1024,
):
    # Create fresh checkpointer and graph inside a single async scope
    async with AsyncPostgresSaver.from_conn_string(DB_URL) as saver:
        await saver.setup()
        graph_inst = await create_graph(saver)
        
        config = {
            "configurable": {
                "thread_id": thread_id,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
        }
        
        async for mode, data in graph_inst.astream(
            {"messages": [HumanMessage(content=message)]},
            config=config,
            stream_mode=["updates"],
        ):
            if mode == "updates":
                if "chat_llm" in data:
                    msg = data["chat_llm"]["messages"][-1]
                    
                    # 1. Handle Tool Calls
                    if hasattr(msg, "tool_calls") and msg.tool_calls:
                        tool_names = [tc["name"] for tc in msg.tool_calls]
                        yield {"type": "tool_call", "names": tool_names}
                    
                    # 2. Handle Text Content
                    if msg.content:
                        text = ""
                        if isinstance(msg.content, str):
                            text = msg.content
                        elif isinstance(msg.content, list):
                            for block in msg.content:
                                if isinstance(block, dict) and block.get("type") == "text":
                                    text += block.get("text", "")
                                elif isinstance(block, str):
                                    text += block
                        if text:
                            yield {"type": "text", "content": text}
                
                elif "tools" in data:
                    yield {"type": "tool", "status": "executing"}

async def get_chat_history(thread_id: str):
    async with AsyncPostgresSaver.from_conn_string(DB_URL) as saver:
        await saver.setup()
        graph_inst = await create_graph(saver)
        config = {"configurable": {"thread_id": thread_id}}
        state = await graph_inst.aget_state(config)
        if state.values:
            return state.values.get("messages", [])
        return []

async def get_all_threads():
    try:
        import asyncpg
        conn = await asyncpg.connect(DB_URL)
        try:
            rows = await conn.fetch("SELECT DISTINCT thread_id FROM checkpoints")
            return [row['thread_id'] for row in rows]
        finally:
            await conn.close()
    except Exception as e:
        print(f"Error fetching threads: {e}")
        return []
