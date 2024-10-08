from collections.abc import AsyncIterator
import math

from sqlalchemy import event, inspect
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app import models


def acos(x):
    return math.acos(x)


def cos(x):
    return math.cos(x)


def sin(x):
    return math.sin(x)


def radians(x):
    return math.radians(x)


def register_math_functions(dbapi_conn, connection_record):
    dbapi_conn.create_function('acos', 1, acos)
    dbapi_conn.create_function('cos', 1, cos)
    dbapi_conn.create_function('sin', 1, sin)
    dbapi_conn.create_function('radians', 1, radians)
    print("Registered 'acos', 'cos', 'sin', and 'radians' functions.")


async_engine = create_async_engine('sqlite+aiosqlite:///db.sqlite3', echo=True)

# Add an event listener to the synchronous connection phase
event.listen(async_engine.sync_engine, 'connect', register_math_functions)

async_session = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)


async def init_models():
    async with async_engine.begin() as conn:
        # Use run_sync to run blocking operations
        await conn.run_sync(check_existing_tables_and_create)


# Synchronous function to check existing tables and create if necessary
def check_existing_tables_and_create(sync_conn):
    inspector = inspect(sync_conn)
    existing_tables = inspector.get_table_names()

    if not existing_tables:
        models.Base.metadata.create_all(sync_conn)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with async_session() as session:
        yield session
