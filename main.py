from contextlib import asynccontextmanager

from fastapi import FastAPI
from routers import (
    auth_router,
    reporting_router,
    section_router,
    session_router,
    user_router,
)
from database import close_database, connect_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    connect_database()
    try:
        yield
    finally:
        close_database()


app = FastAPI(
    title="GPS Attendance System API",
    lifespan=lifespan,
)

app.include_router(auth_router.router)
app.include_router(reporting_router.router)
app.include_router(section_router.router)
app.include_router(session_router.router)
app.include_router(user_router.router)


@app.get("/")
def root():
    return {"message": "GPS Attendance System API is running successfully!"}
