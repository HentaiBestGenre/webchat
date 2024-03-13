from fastapi import Request, WebSocket

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

from backend.core.config import CONNECTION_STRING

engine = create_async_engine(CONNECTION_STRING)
AsyncSessionLocal =  sessionmaker(engine, class_=AsyncSession, expire_on_commit=False) 


async def get_repository(request: Request):
    return request.app.state.repository

async def get_repository_ws(request: WebSocket):
    return request.app.state.repository

async def get_manager(request: Request):
    return request.app.state.manager

async def get_manager_ws(request: WebSocket):
    return request.app.state.manager

async def get_session():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except:
            await session.rollback()
        finally:
            await session.close()