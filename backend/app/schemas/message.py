from datetime import datetime

from pydantic import BaseModel

from enum import Enum


class MessageRole(str, Enum):
    USER = "user"
    SYSTEM = "system"


class Message(BaseModel):
    id: str | None = None
    body: str
    user_id: str
    role: MessageRole
    created_at: datetime | None = None


class MessageRequest(BaseModel):
    body: str