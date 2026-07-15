from fastapi import FastAPI
from sqlalchemy import text

from app.database.base import Base
from app.database.database import engine
from app.models import User
from app.routers.auth import router as auth_router
from app.routers.users import router as users_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CloudRide API",
    description="Cloud-Based Bus Ticketing & Payment System",
    version="1.0.0",
)

app.include_router(auth_router)
app.include_router(users_router)


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