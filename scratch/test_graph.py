import asyncio
import os
from backend.graph import run_graph
from dotenv import load_dotenv

load_dotenv()

async def test():
    print("Starting test...")
    try:
        async for chunk in run_graph("hi", "test_thread_99"):
            print(f"CHUNK: {chunk}")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(test())
