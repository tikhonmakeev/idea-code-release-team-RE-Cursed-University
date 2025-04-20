from datetime import datetime

import sqlalchemy.orm as so
import sqlalchemy as sa

from app.schemas.message import Message, MessageRole

from app.orm_models.base import BaseORM


class MessageORM(BaseORM):
    __tablename__ = "messages"

    body: so.Mapped[str] = so.mapped_column(sa.String)
    role: so.Mapped[MessageRole] = so.mapped_column(sa.Enum(MessageRole))
    user_id: so.Mapped[str] = so.mapped_column(sa.ForeignKey("users.id"))
    created_at: so.Mapped[datetime] = so.mapped_column(sa.DateTime(timezone=True), server_default=sa.func.now())

    def to_message(self) -> Message:
        return Message(
            id=str(self.id), user_id=str(self.user_id), body=self.body, role=self.role, created_at=self.created_at
        )