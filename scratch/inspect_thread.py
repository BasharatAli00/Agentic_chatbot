import asyncio
import sys
import os
from langchain_core.messages import ToolMessage, AIMessage

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

# Set event loop policy
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from graph import create_graph
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

async def inspect_thread(thread_id: str):
    async with AsyncSqliteSaver.from_conn_string("chatbot.db") as saver:
        graph = await create_graph(saver)
        config = {"configurable": {"thread_id": thread_id}}
        state = await graph.aget_state(config)
        
        print(f"--- History for Thread: {thread_id} ---")
        if not state.values:
            print("No history found.")
            return

        messages = state.values.get("messages", [])
        for i, msg in enumerate(messages):
            print(f"{i}: {type(msg).__name__}")
            if isinstance(msg, AIMessage) and msg.tool_calls:
                print(f"   Tool Calls: {[tc['name'] for tc in msg.tool_calls]}")
            if isinstance(msg, ToolMessage):
                print(f"   Tool ID: {msg.tool_call_id}")
        
        # Check for hanging tool calls
        last_ai_with_tools = None
        for msg in messages:
            if isinstance(msg, AIMessage) and msg.tool_calls:
                last_ai_with_tools = msg
            elif isinstance(msg, ToolMessage):
                # If we see a tool message, it might be answering the last AI message
                # For simplicity, we just check the very last message in the next step
                pass
        
        if last_ai_with_tools:
            # Check if all tool calls in last_ai_with_tools have a corresponding ToolMessage
            tool_call_ids = {tc['id'] for tc in last_ai_with_tools.tool_calls}
            tool_msg_ids = {msg.tool_call_id for msg in messages if isinstance(msg, ToolMessage)}
            
            missing = tool_call_ids - tool_msg_ids
            if missing:
                print(f"\n[!] ALERT: Missing tool responses for IDs: {missing}")
                print("This is likely causing the 400 error.")
            else:
                print("\nNo hanging tool calls detected in historical messages.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        tid = sys.argv[1]
    else:
        tid = "thread-1" # Default
    asyncio.run(inspect_thread(tid))
