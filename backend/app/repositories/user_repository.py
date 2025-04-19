from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy.exc import IntegrityError

import sqlalchemy as sa

from app.orm_models.user import UserORM
from app.repositories.exc import NotUniqueException
from app.schemas.user import UserAuth, User


class UserRepository:
    session_maker: async_sessionmaker[AsyncSession]

    def __init__(self, session_maker: async_sessionmaker[AsyncSession]):
        self.session_maker = session_maker

    async def create_user(self, user_auth: UserAuth) -> User:
        async with self.session_maker() as session:
            user_entry = UserORM(login=user_auth.login, password_hash=user_auth.password_hash)
            session.add(user_entry)
            try:
                await session.commit()
                await session.refresh(user_entry)
                return user_entry.to_user()
            except IntegrityError:
                raise NotUniqueException

    async def get_user_by_login(self, login: str) -> User | None:
        async with self.session_maker() as session:
            query = sa.select(UserORM).where(UserORM.login == login)
            user_entry = await session.scalar(query)
            if not user_entry:
                return None
            return user_entry.to_user()
