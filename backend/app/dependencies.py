from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBasicCredentials, HTTPBasic

from app.repositories.user_repository import UserRepository
from app.schemas.user import UserAuth, User
from app.services.user_service import UserService
from app.services.exc import AuthException

from app.core.database import SessionLocal


def get_user_service() -> UserService:
    return UserService(UserRepository(SessionLocal))


def get_user_auth(credentials: Annotated[HTTPBasicCredentials, Depends(HTTPBasic())]) -> UserAuth:
    return UserAuth(username=credentials.username, password=credentials.password)


async def get_user(user_auth: Annotated[UserAuth, Depends(get_user_auth)],
                   user_service: Annotated[UserService, Depends(get_user_service)]) -> User:
    try:
        user = await user_service.auth_user(user_auth)
        return user
    except AuthException:
        raise HTTPException(401)