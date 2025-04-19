from pydantic import BaseModel

from enum import Enum


class MessageRole(str, Enum):
    USER = "user"
    SYSTEM = "system"


class Message(BaseModel):
    id: str
    body: str
    user_id: str
    role: MessageRole


class MessageRequest(BaseModel):
    body: str