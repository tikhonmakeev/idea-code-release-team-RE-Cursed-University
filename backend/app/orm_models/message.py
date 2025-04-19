import sqlalchemy.orm as so
import sqlalchemy as sa

from app.schemas.message import Message, MessageRole

from app.orm_models.base import BaseORM


class MessageORM(BaseORM):
    __tablename__ = "messages"

    body: so.Mapped[str] = so.mapped_column(sa.String)
    role: so.Mapped[MessageRole] = so.mapped_column(sa.Enum(MessageRole))
    user_id: so.Mapped[str] = so.mapped_column(sa.ForeignKey("users.id"))

    def to_message(self) -> Message:
        return Message(
            id=self.id, body=self.body, role=self.role
        )