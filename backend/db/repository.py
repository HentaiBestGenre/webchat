from backend.models import UserInDB
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.db.schemas import User, Messages
from backend.servises import hash_password


class Repo:

    async def get_user(self, session: AsyncSession, id: int):
        query = select(User).where(User.id == id)   
        result = await session.execute(query)
        user = result.scalars().first()
        return user
    
    async def get_user_by_username(self, session: AsyncSession, username: str):
        query = select(User).where(User.username == username)
        result = await session.execute(query)
        user = result.scalars().first()
        return user
    
    async def get_messages(self, session: AsyncSession):
        query = select(Messages).order_by(Messages.created_at.asc())
        result = await session.execute(query)
        return result.fetchall()
    
    async def add_messages(self, session: AsyncSession, user_id, content, user_name) -> Messages:
        message = Messages(
            user_id = user_id,
            content = content,
            user_name = user_name,
            created_at = datetime.now()
        )

        session.add(message)
        await session.flush()
        await session.refresh(message)
        return message
    
    async def create_user(self, session: AsyncSession, username, password):
        hashed_password = hash_password(password)

        user = User(username=username, hashed_password=hashed_password)
        session.add(user)
        await session.flush()
        await session.refresh(user)
        return user

    async def delete_message(self, session, message_id):
        query = select(Messages).where(Messages.id == message_id)
        result = await session.execute(query)
        message_to_delete = result.scalars().first()

        if message_to_delete:
            await session.delete(message_to_delete)
            await session.flush()
            return message_to_delete
        return message_to_delete
    
    async def update_message(self, session, message_id, content):
        query: Messages = select(Messages).where(Messages.id == message_id)
        result = await session.execute(query)
        message_to_update = result.scalars().first()

        if message_to_update:
            message_to_update.content = content
            await session.flush()
            await session.refresh(message_to_update)
        return message_to_update
    