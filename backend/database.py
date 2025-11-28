import os
from contextlib import asynccontextmanager
from psycopg_pool import AsyncConnectionPool

DB_URI = os.getenv("DATABASE_URL", "postgresql://user:password@postgres:5432/agent_db")

@asynccontextmanager
async def get_db_connection():
    async with AsyncConnectionPool(conninfo=DB_URI) as pool:
        async with pool.connection() as conn:
            yield conn
