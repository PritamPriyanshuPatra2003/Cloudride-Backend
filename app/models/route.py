from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Route(Base):
    __tablename__ = "routes"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    source_city: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    destination_city: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    distance_km: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    estimated_duration: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )