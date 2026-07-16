from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class BookingCreate(BaseModel):
    schedule_id: int = Field(gt=0)
    seat_number: str = Field(min_length=1, max_length=10)
    passenger_name: str = Field(min_length=2, max_length=100)
    passenger_age: int = Field(gt=0, le=120)
    passenger_gender: str = Field(min_length=1, max_length=20)


class BookingResponse(BaseModel):
    id: int
    booking_reference: str
    user_id: int
    schedule_id: int
    seat_number: str
    passenger_name: str
    passenger_age: int
    passenger_gender: str
    booking_status: str
    total_amount: Decimal
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)