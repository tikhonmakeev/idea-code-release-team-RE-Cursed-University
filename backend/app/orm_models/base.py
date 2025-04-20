import sqlalchemy as sa
import sqlalchemy.orm as so

import uuid


class BaseORM(so.DeclarativeBase):
    id: so.Mapped[uuid.UUID] = so.mapped_column(
        sa.UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True
    )