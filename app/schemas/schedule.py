from datetime import date, datetime, time
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ScheduleCreate(BaseModel):
    bus_id: int = Field(gt=0)
    route_id: int = Field(gt=0)
    journey_date: date
    departure_time: time
    arrival_time: time
    fare: Decimal = Field(gt=0, max_digits=10, decimal_places=2)


class ScheduleUpdate(BaseModel):
    journey_date: date | None = None
    departure_time: time | None = None
    arrival_time: time | None = None
    fare: Decimal | None = Field(
        default=None,
        gt=0,
        max_digits=10,
        decimal_places=2,
    )
    is_active: bool | None = None


class ScheduleResponse(BaseModel):
    id: int
    bus_id: int
    route_id: int
    journey_date: date
    departure_time: time
    arrival_time: time
    fare: Decimal
    available_seats: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)