from fastapi import APIRouter
from services.attendance_service import open_session_db

router = APIRouter(prefix="/api", tags=["Sessions"])


@router.post("/classes/{id}/sessions", status_code=201)
def open_session(id: str, req: dict):
    result = open_session_db(id, req)
    return {"success": True, "message": "Attendance session opened successfully", "data": result}
