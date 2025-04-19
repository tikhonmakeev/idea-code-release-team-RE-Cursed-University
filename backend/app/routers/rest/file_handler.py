from http import HTTPStatus

from fastapi import APIRouter, UploadFile
from fastapi.responses import FileResponse
from websockets.legacy.server import HTTPResponse

from app.repositories.file_repository import create_file, check_file_exists_by_user
import os


BASE_USER_FILES_DIR = os.getenv('BASE_USER_FILES_DIR', '/user_files')

router = APIRouter(prefix="/file")

@router.post("/upload")
async def upload_file(file: UploadFile):
  # TODO: Прописать бизнес-логику БД
  await create_file(BASE_USER_FILES_DIR, file.file, file.filename)
  return HTTPResponse(HTTPStatus.CREATED)

@router.get("/download/{filename}")
def download_file(filename: str):
  # TODO: Прописать бизнес-логику БД, прочекать, принадлежит ли файл юзеру
  # Дальше по юзеру и названию ищем файл и возвращаем
  if not check_file_exists_by_user:
    return HTTPResponse(HTTPStatus.NOT_FOUND)
  return FileResponse(path='путь к файлу юзера', filename=filename, media_type='multipart/form-data')
