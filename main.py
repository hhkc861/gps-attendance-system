from contextlib import asynccontextmanager

from fastapi import FastAPI
from routers import auth, user, academic, session, attendance, reporting
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

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(academic.router)
app.include_router(session.router)
app.include_router(attendance.router)
app.include_router(reporting.router)


@app.get("/")
def root():
    return {"message": "GPS Attendance System API is running successfully!"}
