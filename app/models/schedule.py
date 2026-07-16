from datetime import date, datetime, time
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    Time,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Schedule(Base):
    __tablename__ = "schedules"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    bus_id: Mapped[int] = mapped_column(
        ForeignKey("buses.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    route_id: Mapped[int] = mapped_column(
        ForeignKey("routes.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    journey_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
    )

    departure_time: Mapped[time] = mapped_column(
        Time,
        nullable=False,
    )

    arrival_time: Mapped[time] = mapped_column(
        Time,
        nullable=False,
    )

    fare: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    available_seats: Mapped[int] = mapped_column(
        Integer,
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
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    bus = relationship("Bus")
    route = relationship("Route")