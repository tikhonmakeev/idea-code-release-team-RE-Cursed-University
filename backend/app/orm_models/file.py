from datetime import datetime

import sqlalchemy.orm as so
import sqlalchemy as sa

from app.orm_models.base import BaseORM
from app.schemas.file import File


class FileORM(BaseORM):
    __tablename__ = "files"

    filename: so.Mapped[str] = so.mapped_column(sa.String)
    user_id: so.Mapped[str] = so.mapped_column(sa.ForeignKey("users.id"))
    created_at: so.Mapped[datetime] = so.mapped_column(sa.DateTime(timezone=True), server_default=sa.func.now())

    def to_file(self) -> File:
        return File(
            id=str(self.id), user_id=str(self.user_id), filename=self.filename, created_at=self.created_at
        )