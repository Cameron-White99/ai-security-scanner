import uuid
from datetime import datetime
from sqlalchemy import DateTime, Integer, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from db.database import Base


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    from_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    to_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    total_scans: Mapped[int] = mapped_column(Integer, nullable=False)
    data: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
