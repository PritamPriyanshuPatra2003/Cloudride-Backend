from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class BusCreate(BaseModel):
    bus_number: str = Field(min_length=3, max_length=30)
    bus_name: str = Field(min_length=2, max_length=100)
    operator_name: str = Field(min_length=2, max_length=100)
    bus_type: str = Field(min_length=2, max_length=50)
    total_seats: int = Field(gt=0, le=100)


class BusUpdate(BaseModel):
    bus_name: str | None = Field(default=None, min_length=2, max_length=100)
    operator_name: str | None = Field(default=None, min_length=2, max_length=100)
    bus_type: str | None = Field(default=None, min_length=2, max_length=50)
    total_seats: int | None = Field(default=None, gt=0, le=100)
    is_active: bool | None = None


class BusResponse(BaseModel):
    id: int
    bus_number: str
    bus_name: str
    operator_name: str
    bus_type: str
    total_seats: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)