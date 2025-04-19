from typing import Annotated

from fastapi import APIRouter, Depends

from app.dependencies import get_user, get_message_service
from app.schemas.message import MessageRequest, Message, MessageRole
from app.schemas.user import User
from app.services.message_service import MessageService

router = APIRouter(prefix="/api/v1/messages", tags=["messages"])


@router.post("")
async def send_message(message: MessageRequest,
                       user: Annotated[User, Depends(get_user)],
                       message_service: Annotated[MessageService, Depends(get_message_service)]) -> Message:
    user_message = Message(body=message.body, user_id=user.id, role=MessageRole.USER)
    await message_service.create_message(user_message)
    system_message = Message(body=f"message from user {user.id}", user_id=user.id, role=MessageRole.SYSTEM)
    return await message_service.create_message(system_message)


@router.get("/history")
async def get_history(user: Annotated[User, Depends(get_user)],
                       message_service: Annotated[MessageService, Depends(get_message_service)]) -> list[Message]:
    return await message_service.get_messages_of(user)
