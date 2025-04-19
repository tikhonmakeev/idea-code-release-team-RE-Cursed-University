from app.repositories.message_repository import MessageRepository
from app.schemas.message import Message
from app.schemas.user import User


class MessageService:
    def __init__(self, message_repository: MessageRepository):
        self.message_repository = message_repository

    async def create_message(self, message: Message) -> Message:
        return await self.message_repository.create_message(message)

    async def get_messages_of(self, user: User) -> list[Message]:
        return await self.message_repository.get_messages_of(user)