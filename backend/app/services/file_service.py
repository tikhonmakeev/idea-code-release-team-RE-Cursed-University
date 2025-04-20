from app.repositories.file_repository import FileRepository
from app.schemas.file import File
from app.schemas.user import User
from fastapi import UploadFile

from app.core.config import BASE_USER_FILES_DIR

class FileService:
    def __init__(self, file_repository: FileRepository):
        self.file_repository = file_repository

    async def create_file(self, user_id: str, file: UploadFile) -> File:
        return await self.file_repository.create_file(BASE_USER_FILES_DIR, user_id, file.filename, file.file)

    async def get_files_of(self, user: User) -> list[File]:
        return await self.file_repository.get_files_of(user)

    @staticmethod
    def check_file_exists_locally_by_user(user_id: str, filename: str):
        return FileRepository.check_file_exists_locally_by_user(BASE_USER_FILES_DIR, user_id, filename)