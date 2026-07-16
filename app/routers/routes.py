from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.dependencies import get_current_admin, get_current_user
from app.models.route import Route
from app.models.user import User
from app.schemas.route import RouteCreate, RouteResponse, RouteUpdate

router = APIRouter(
    prefix="/routes",
    tags=["Routes"],
)


@router.post(
    "",
    response_model=RouteResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_route(
    route_data: RouteCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    source = route_data.source_city.strip().title()
    destination = route_data.destination_city.strip().title()

    existing_route = db.scalar(
        select(Route).where(
            func.lower(Route.source_city) == source.lower(),
            func.lower(Route.destination_city) == destination.lower(),
        )
    )

    if existing_route:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Route already exists",
        )

    new_route = Route(
        source_city=source,
        destination_city=destination,
        distance_km=route_data.distance_km,
        estimated_duration=route_data.estimated_duration.strip(),
    )

    db.add(new_route)
    db.commit()
    db.refresh(new_route)

    return new_route


@router.get(
    "",
    response_model=list[RouteResponse],
)
def list_routes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    routes = db.scalars(
        select(Route).order_by(Route.created_at.desc())
    ).all()

    return list(routes)


@router.get(
    "/{route_id}",
    response_model=RouteResponse,
)
def get_route(
    route_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    route = db.get(Route, route_id)

    if route is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Route not found",
        )

    return route


@router.put(
    "/{route_id}",
    response_model=RouteResponse,
)
def update_route(
    route_id: int,
    route_data: RouteUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    route = db.get(Route, route_id)

    if route is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Route not found",
        )

    update_data = route_data.model_dump(exclude_unset=True)

    if "source_city" in update_data:
        update_data["source_city"] = update_data["source_city"].strip().title()

    if "destination_city" in update_data:
        update_data["destination_city"] = (
            update_data["destination_city"].strip().title()
        )

    final_source = update_data.get("source_city", route.source_city)
    final_destination = update_data.get(
        "destination_city",
        route.destination_city,
    )

    if final_source.lower() == final_destination.lower():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Source and destination cities must be different",
        )

    for field, value in update_data.items():
        setattr(route, field, value)

    db.commit()
    db.refresh(route)

    return route


@router.delete(
    "/{route_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_route(
    route_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    route = db.get(Route, route_id)

    if route is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Route not found",
        )

    db.delete(route)
    db.commit()