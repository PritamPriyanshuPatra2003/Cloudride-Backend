from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.dependencies import get_current_admin, get_current_user
from app.models.bus import Bus
from app.models.route import Route
from app.models.schedule import Schedule
from app.models.user import User
from app.schemas.schedule import (
    ScheduleCreate,
    ScheduleResponse,
    ScheduleUpdate,
)

router = APIRouter(
    prefix="/schedules",
    tags=["Schedules"],
)


@router.post(
    "",
    response_model=ScheduleResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_schedule(
    schedule_data: ScheduleCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    bus = db.get(Bus, schedule_data.bus_id)

    if bus is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bus not found",
        )

    if not bus.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Selected bus is inactive",
        )

    route = db.get(Route, schedule_data.route_id)

    if route is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Route not found",
        )

    if not route.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Selected route is inactive",
        )

    if schedule_data.journey_date < date.today():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Journey date cannot be in the past",
        )

    if schedule_data.arrival_time == schedule_data.departure_time:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Arrival and departure times cannot be the same",
        )

    existing_schedule = db.scalar(
        select(Schedule).where(
            Schedule.bus_id == schedule_data.bus_id,
            Schedule.journey_date == schedule_data.journey_date,
            Schedule.departure_time == schedule_data.departure_time,
        )
    )

    if existing_schedule:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This bus already has a schedule at the selected date and time",
        )

    new_schedule = Schedule(
        bus_id=schedule_data.bus_id,
        route_id=schedule_data.route_id,
        journey_date=schedule_data.journey_date,
        departure_time=schedule_data.departure_time,
        arrival_time=schedule_data.arrival_time,
        fare=schedule_data.fare,
        available_seats=bus.total_seats,
    )

    db.add(new_schedule)
    db.commit()
    db.refresh(new_schedule)

    return new_schedule


@router.get(
    "",
    response_model=list[ScheduleResponse],
)
def list_schedules(
    journey_date: date | None = Query(default=None),
    route_id: int | None = Query(default=None, gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    statement = select(Schedule)

    if journey_date is not None:
        statement = statement.where(
            Schedule.journey_date == journey_date
        )

    if route_id is not None:
        statement = statement.where(
            Schedule.route_id == route_id
        )

    schedules = db.scalars(
        statement.order_by(
            Schedule.journey_date,
            Schedule.departure_time,
        )
    ).all()

    return list(schedules)


@router.get(
    "/{schedule_id}",
    response_model=ScheduleResponse,
)
def get_schedule(
    schedule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    schedule = db.get(Schedule, schedule_id)

    if schedule is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found",
        )

    return schedule


@router.put(
    "/{schedule_id}",
    response_model=ScheduleResponse,
)
def update_schedule(
    schedule_id: int,
    schedule_data: ScheduleUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    schedule = db.get(Schedule, schedule_id)

    if schedule is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found",
        )

    update_data = schedule_data.model_dump(exclude_unset=True)

    final_date = update_data.get(
        "journey_date",
        schedule.journey_date,
    )
    final_departure = update_data.get(
        "departure_time",
        schedule.departure_time,
    )
    final_arrival = update_data.get(
        "arrival_time",
        schedule.arrival_time,
    )

    if final_date < date.today():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Journey date cannot be in the past",
        )

    if final_departure == final_arrival:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Arrival and departure times cannot be the same",
        )

    for field, value in update_data.items():
        setattr(schedule, field, value)

    db.commit()
    db.refresh(schedule)

    return schedule


@router.delete(
    "/{schedule_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_schedule(
    schedule_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    schedule = db.get(Schedule, schedule_id)

    if schedule is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found",
        )

    db.delete(schedule)
    db.commit()