import os
from typing import BinaryIO

import aiofiles
import aiofiles.os as aios
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
import sqlalchemy as sa

from app.orm_models.file import FileORM
from app.repositories.exc import ConstraintViolationException
from app.schemas.file import File
from app.schemas.user import User
from app.core.config import BASE_USER_FILES_DIR


class FileRepository:
    session_maker: async_sessionmaker[AsyncSession]

    def __init__(self, session_maker: async_sessionmaker[AsyncSession]):
        self.session_maker = session_maker

    @staticmethod
    async def create_users_folder_if_not_exists():
        folder_path = BASE_USER_FILES_DIR
        if not await aios.path.exists(folder_path):
            await aios.mkdir(folder_path)

    async def create_file(self, base_dir: str, user_id: str, filename: str, file: BinaryIO):
        await self.create_users_folder_if_not_exists()

        folder_path = os.path.join(base_dir, user_id)
        if not await aios.path.exists(folder_path):
            await aios.mkdir(folder_path)

        if await self.check_file_exists_locally_by_user(base_dir, user_id, filename):
            raise HTTPException(status_code=400)

        file_path = os.path.join(folder_path, filename)
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(file.read())

        async with self.session_maker() as session:
            file_entry = FileORM(filename=filename, user_id=user_id)
            session.add(file_entry)
            try:
                await session.commit()
                await session.refresh(file_entry)
                return file_entry.to_file()
            except IntegrityError:
                raise ConstraintViolationException

    @staticmethod
    async def check_file_exists_locally_by_user(base_dir: str, user_id: str, filename: str):
        file_path = os.path.join(base_dir, user_id, filename)
        return await aios.path.exists(file_path)

    async def get_files_of(self, user: User) -> list[File]:
        async with self.session_maker() as session:
            query = sa.select(FileORM).where(FileORM.user_id == user.id)
            result = await session.execute(query)
            entries = result.scalars().all()
            return [entry.to_file() for entry in entries]