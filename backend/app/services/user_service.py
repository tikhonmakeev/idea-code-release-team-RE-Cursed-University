from passlib.hash import bcrypt

from app.repositories.exc import ConstraintViolationException
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserAuth, User
from app.services.exc import NotUniqueException, AuthException


class UserService:
    user_repository: UserRepository

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def register_user(self, user_auth: UserAuth) -> User:
        user_auth.password_hash = bcrypt.hash(user_auth.password)
        try:
            user = await self.user_repository.create_user(user_auth)
            return user
        except ConstraintViolationException:
            raise NotUniqueException

    async def auth_user(self, user_auth: UserAuth) -> User:
        user_entry = await self.user_repository.get_user_by_login(user_auth.login)
        if user_entry is None:
            raise AuthException
        if not bcrypt.verify(user_auth.password, user_entry.password_hash):
            raise AuthException
        return user_entry.to_user()
