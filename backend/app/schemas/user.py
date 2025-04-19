from pydantic import BaseModel


class User(BaseModel):
    id: str
    login: str
    password_hash: str


class UserAuth(BaseModel):
    login: str
    password: str


class UserResponse(BaseModel):
    id: str
    login: str

    @classmethod
    def from_user(cls, user: User) -> "UserResponse":
        return cls(id=user.id, login=user.login)