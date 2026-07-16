from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


class RouteCreate(BaseModel):
    source_city: str = Field(min_length=2, max_length=100)
    destination_city: str = Field(min_length=2, max_length=100)
    distance_km: int = Field(gt=0)
    estimated_duration: str = Field(min_length=2, max_length=20)

    @model_validator(mode="after")
    def validate_cities(self):
        if self.source_city.strip().lower() == self.destination_city.strip().lower():
            raise ValueError("Source and destination cities must be different")
        return self


class RouteUpdate(BaseModel):
    source_city: str | None = Field(default=None, min_length=2, max_length=100)
    destination_city: str | None = Field(default=None, min_length=2, max_length=100)
    distance_km: int | None = Field(default=None, gt=0)
    estimated_duration: str | None = Field(default=None, min_length=2, max_length=20)
    is_active: bool | None = None


class RouteResponse(BaseModel):
    id: int
    source_city: str
    destination_city: str
    distance_km: int
    estimated_duration: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)