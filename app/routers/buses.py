from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.dependencies import get_current_admin, get_current_user
from app.models.bus import Bus
from app.models.user import User
from app.schemas.bus import BusCreate, BusResponse, BusUpdate

router = APIRouter(
    prefix="/buses",
    tags=["Buses"],
)


@router.post(
    "",
    response_model=BusResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_bus(
    bus_data: BusCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    existing_bus = db.scalar(
        select(Bus).where(
            Bus.bus_number == bus_data.bus_number.upper()
        )
    )

    if existing_bus:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Bus number already exists",
        )

    new_bus = Bus(
        bus_number=bus_data.bus_number.upper(),
        bus_name=bus_data.bus_name.strip(),
        operator_name=bus_data.operator_name.strip(),
        bus_type=bus_data.bus_type.strip(),
        total_seats=bus_data.total_seats,
    )

    db.add(new_bus)
    db.commit()
    db.refresh(new_bus)

    return new_bus


@router.get(
    "",
    response_model=list[BusResponse],
)
def list_buses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    buses = db.scalars(
        select(Bus).order_by(Bus.created_at.desc())
    ).all()

    return list(buses)


@router.get(
    "/{bus_id}",
    response_model=BusResponse,
)
def get_bus(
    bus_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    bus = db.get(Bus, bus_id)

    if bus is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bus not found",
        )

    return bus


@router.put(
    "/{bus_id}",
    response_model=BusResponse,
)
def update_bus(
    bus_id: int,
    bus_data: BusUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    bus = db.get(Bus, bus_id)

    if bus is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bus not found",
        )

    update_data = bus_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(bus, field, value)

    db.commit()
    db.refresh(bus)

    return bus


@router.delete(
    "/{bus_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_bus(
    bus_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    bus = db.get(Bus, bus_id)

    if bus is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bus not found",
        )

    db.delete(bus)
    db.commit()