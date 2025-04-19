from typing import Annotated

from fastapi import APIRouter, UploadFile, Depends, status, HTTPException
from fastapi.responses import FileResponse

from app.dependencies import get_user
from app.repositories.file_repository import create_file, check_file_exists_by_user
import os

from app.schemas.user import User

BASE_USER_FILES_DIR = os.getenv('BASE_USER_FILES_DIR', '/user_files')

router = APIRouter(prefix="/files")

@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_file(user: Annotated[User, Depends(get_user)], file: UploadFile):
  # TODO: Прописать бизнес-логику БД
  await create_file(BASE_USER_FILES_DIR, user.id, file.filename, file.file)

@router.get("/download/{filename}")
def download_file(user: Annotated[User, Depends(get_user)], filename: str):
  # TODO: Прописать бизнес-логику БД, прочекать
  if not check_file_exists_by_user(BASE_USER_FILES_DIR, user.id, filename):
    raise HTTPException(status_code=404)
  return FileResponse(path='путь к файлу юзера', filename=filename, media_type='multipart/form-data')
