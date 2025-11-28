import asyncio
import os
import sys
from pathlib import Path

# Add backend to path so imports work
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

from agent.graph import pool
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

async def main():
    print("Initializing database tables...")
    # We can use the pool directly or create a new one.
    # Since we are in a standalone script, let's just use the saver's setup.
    # But we need to make sure the pool is open.
    await pool.open()
    async with AsyncPostgresSaver(pool) as checkpointer:
        await checkpointer.setup()
    await pool.close()
    print("Done!")

if __name__ == "__main__":
    asyncio.run(main())
