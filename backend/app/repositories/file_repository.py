import os
import aiofiles
from fastapi import UploadFile, HTTPException


async def create_file(base_dir: str, user_id: str, filename: str, file: UploadFile.file):
    folder_path = os.path.join(base_dir, user_id)
    if os.path.exists(folder_path):
        os.mkdir(folder_path)

    if check_file_exists_by_user(base_dir, user_id, file.filename):
        raise HTTPException(status_code=400)

    file_path = os.path.join(folder_path, filename)
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(file)

    return file_path


def check_file_exists_by_user(base_dir: str, user_id: str, filename: str):
    folder_path = os.path.join(base_dir, user_id)
    file_path = os.path.join(folder_path, filename)
    return os.path.exists(file_path)