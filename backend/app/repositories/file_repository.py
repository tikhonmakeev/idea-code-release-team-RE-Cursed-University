import os
from fastapi import UploadFile


async def create_file(base_dir: str, user_id: str, filename: str, file: UploadFile.file):
    folder_path = os.path.join(base_dir, user_id)
    if os.path.exists(folder_path):
        os.mkdir(folder_path)

    file_path = os.path.join(folder_path, filename)
    with open(file_path, "wb") as f:
        f.write(file)

    return file_path


async def check_file_exists_by_user(base_dir: str, user_id: str, filename: str):
    folder_path = os.path.join(base_dir, user_id)
    return os.path.exists(folder_path)