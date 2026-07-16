from fastapi import FastAPI
from sqlalchemy import text

from app.database.base import Base
from app.database.database import engine
from app.models import Booking, Bus, Route, Schedule, User
from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.routers.buses import router as buses_router
from app.routers.routes import router as routes_router
from app.routers.schedules import router as schedules_router
from app.routers.bookings import router as bookings_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CloudRide API",
    description="Cloud-Based Bus Ticketing & Payment System",
    version="1.0.0",
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(buses_router)
app.include_router(routes_router)
app.include_router(schedules_router)
app.include_router(bookings_router)


@app.get("/")
def root():
    return {
        "status": "success",
        "message": "Welcome to CloudRide API 🚍",
    }


@app.get("/health")
def health():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "status": "healthy",
            "database": "connected",
        }

    except Exception as error:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(error),
        }