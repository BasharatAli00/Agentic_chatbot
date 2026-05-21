from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
import json
import asyncio
import sys

# Windows + Python 3.12 compatibility
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from graph import run_graph, get_chat_history, get_all_threads

app = FastAPI(title="Agentic Chatbot API")

# Global graph initialization removed to ensure fresh lifecycle per request

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    thread_id: str
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 1024

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    async def event_generator():
        try:
            # run_graph is now an async generator
            async for chunk in run_graph(
                message=request.message,
                thread_id=request.thread_id,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
            ):
                # Yield as Server-Sent Event
                yield f"data: {json.dumps(chunk)}\n\n"
                # Small sleep to ensure streaming feel if backend is too fast
                await asyncio.sleep(0.01)
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/api/history/{thread_id}")
async def history_endpoint(thread_id: str):
    try:
        history = await get_chat_history(thread_id)
        # Convert LangChain messages to simple dicts for the frontend
        formatted_history = []
        for m in history:
            role = "user" if m.type == "human" else "assistant"
            if m.content:
                text_content = ""
                if isinstance(m.content, str):
                    text_content = m.content
                elif isinstance(m.content, list):
                    for block in m.content:
                        if isinstance(block, dict) and block.get("type") == "text":
                            text_content += block.get("text", "")
                        elif isinstance(block, str):
                            text_content += block
                
                if text_content:
                    formatted_history.append({"role": role, "content": text_content})
        return formatted_history
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/threads")
async def threads_endpoint():
    try:
        threads = await get_all_threads()
        return {"threads": threads}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
