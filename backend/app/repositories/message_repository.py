from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy.exc import IntegrityError
import sqlalchemy as sa

from app.orm_models.message import MessageORM
from app.repositories.exc import ConstraintViolationException
from app.schemas.message import Message
from app.schemas.user import User


class MessageRepository:
    session_maker: async_sessionmaker[AsyncSession]

    def __init__(self, session_maker: async_sessionmaker[AsyncSession]):
        self.session_maker = session_maker

    async def create_message(self, message: Message) -> Message:
        async with self.session_maker() as session:
            message_entry = MessageORM(body=message.body, user_id=message.user_id, role=message.role)
            session.add(message_entry)
            try:
                await session.commit()
                await session.refresh(message_entry)
                return message_entry.to_message()
            except IntegrityError:
                raise ConstraintViolationException

    async def get_messages_of(self, user: User) -> list[Message]:
        async with self.session_maker() as session:
            query = sa.select(MessageORM).where(MessageORM.user_id == user.id)
            result = await session.execute(query)
            entries = result.scalars().all()
            return [entry.to_message() for entry in entries]