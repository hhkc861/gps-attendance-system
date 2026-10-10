from fastapi import FastAPI
from routers import auth, user, academic, session, attendance, reporting

app = FastAPI(title="GPS Attendance System API", version="1.0")

# Đăng ký các router module
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(academic.router)
app.include_router(session.router)
app.include_router(attendance.router)
app.include_router(reporting.router)

@app.get("/")
def root():
    return {"message": "GPS Attendance System API is running successfully!"}