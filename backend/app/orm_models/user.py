import sqlalchemy as sa
import sqlalchemy.orm as so

from app.orm_models.base import BaseORM
from app.schemas.user import User

class UserORM(BaseORM):
    __tablename__ = "users"

    login: so.Mapped[str] = so.mapped_column(sa.String, unique=True, index=True)
    password_hash: so.Mapped[str]

    def to_user(self) -> User:
        return User(id=self.id, login=self.login, password_hash=self.password_hash)