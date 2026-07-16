import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.dependencies import get_current_user
from app.models.booking import Booking
from app.models.schedule import Schedule
from app.models.user import User
from app.schemas.booking import BookingCreate, BookingResponse

router = APIRouter(
    prefix="/bookings",
    tags=["Bookings"],
)


@router.post(
    "",
    response_model=BookingResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_booking(
    booking_data: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    schedule = db.get(Schedule, booking_data.schedule_id)

    if schedule is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found",
        )

    if not schedule.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Schedule is inactive",
        )

    if schedule.available_seats <= 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No seats available",
        )

    normalized_seat = booking_data.seat_number.strip().upper()

    existing_booking = db.scalar(
        select(Booking).where(
            Booking.schedule_id == schedule.id,
            Booking.seat_number == normalized_seat,
        )
    )

    if (
        existing_booking
        and existing_booking.booking_status != "CANCELLED"
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Seat is already booked",
        )

    booking_reference = f"CR-{uuid.uuid4().hex[:8].upper()}"

    # Reuse the old row when this seat had previously been cancelled.
    if (
        existing_booking
        and existing_booking.booking_status == "CANCELLED"
    ):
        existing_booking.booking_reference = booking_reference
        existing_booking.user_id = current_user.id
        existing_booking.passenger_name = (
            booking_data.passenger_name.strip()
        )
        existing_booking.passenger_age = booking_data.passenger_age
        existing_booking.passenger_gender = (
            booking_data.passenger_gender.strip().title()
        )
        existing_booking.booking_status = "PENDING"
        existing_booking.total_amount = schedule.fare

        try:
            schedule.available_seats -= 1
            db.commit()
            db.refresh(existing_booking)

            return existing_booking

        except Exception:
            db.rollback()

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unable to recreate booking",
            )

    new_booking = Booking(
        booking_reference=booking_reference,
        user_id=current_user.id,
        schedule_id=schedule.id,
        seat_number=normalized_seat,
        passenger_name=booking_data.passenger_name.strip(),
        passenger_age=booking_data.passenger_age,
        passenger_gender=booking_data.passenger_gender.strip().title(),
        booking_status="PENDING",
        total_amount=schedule.fare,
    )

    try:
        db.add(new_booking)
        schedule.available_seats -= 1

        db.commit()
        db.refresh(new_booking)

        return new_booking

    except Exception:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to create booking",
        )


@router.get(
    "",
    response_model=list[BookingResponse],
)
def list_my_bookings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    bookings = db.scalars(
        select(Booking)
        .where(Booking.user_id == current_user.id)
        .order_by(Booking.created_at.desc())
    ).all()

    return list(bookings)


@router.get(
    "/{booking_id}",
    response_model=BookingResponse,
)
def get_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    booking = db.get(Booking, booking_id)

    if booking is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found",
        )

    if booking.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to view this booking",
        )

    return booking


@router.delete(
    "/{booking_id}",
    response_model=BookingResponse,
)
def cancel_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    booking = db.get(Booking, booking_id)

    if booking is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found",
        )

    if booking.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to cancel this booking",
        )

    if booking.booking_status == "CANCELLED":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Booking is already cancelled",
        )

    schedule = db.get(Schedule, booking.schedule_id)

    if schedule is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated schedule not found",
        )

    try:
        booking.booking_status = "CANCELLED"
        schedule.available_seats += 1

        db.commit()
        db.refresh(booking)

        return booking

    except Exception:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to cancel booking",
        )