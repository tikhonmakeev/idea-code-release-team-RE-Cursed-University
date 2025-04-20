from typing import Annotated

import os
from fastapi import APIRouter, UploadFile, Depends, status, HTTPException
from fastapi.responses import FileResponse

from app.core.dependencies import get_user, get_file_service
from app.schemas.file import File
from app.services.file_service import FileService
from app.schemas.user import User
from app.core.config import BASE_USER_FILES_DIR

router = APIRouter(prefix="/api/v1/files")

@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_file(user: Annotated[User, Depends(get_user)], file: UploadFile,
                      file_service: Annotated[FileService, Depends(get_file_service)]) -> File:
  return await file_service.create_file(user.id, file)

@router.get("/download/{filename}")
async def download_file(user: Annotated[User, Depends(get_user)], filename: str,
  file_service: Annotated[FileService, Depends(get_file_service)]) -> FileResponse:

  if not file_service.check_file_exists_locally_by_user(user.id, filename):
    raise HTTPException(status_code=404)

  file_path = os.path.join(BASE_USER_FILES_DIR, user.id, filename)
  return FileResponse(path=file_path, filename=filename, media_type='multipart/form-data')
