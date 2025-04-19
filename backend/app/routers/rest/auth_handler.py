from fastapi import HTTPException
from typing import Annotated

from fastapi import APIRouter, Depends

from app.schemas.user import UserAuth, UserResponse, User
from app.services.exc import NotUniqueException
from app.services.user_service import UserService
from app.dependencies import get_user_service, get_user

router = APIRouter(prefix="/api/v1/auth",
                   tags=["auth"])

@router.post("/register")
async def register_user(user_to_register: UserAuth,
                        user_service: Annotated[UserService, Depends(get_user_service)]) -> UserResponse:
    try:
        user = await user_service.register_user(user_to_register)
        return UserResponse.from_user(user)
    except NotUniqueException:
        raise HTTPException(422, detail="Login already taken")


@router.get("/get_my_info")
async def get_user_info(user: Annotated[User, Depends(get_user)]) -> UserResponse:
    return UserResponse.from_user(user)