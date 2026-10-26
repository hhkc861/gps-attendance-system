from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from database import get_session
from services.attendance_service import process_gps_attendance

router = APIRouter(prefix="/api/attendance", tags=["Attendance"])

@router.post("", status_code=status.HTTP_200_OK)
def mark_attendance(
    session_id: int,
    student_id: int,
    latitude: float,
    longitude: float,
    db: Session = Depends(get_session)
):

    return process_gps_attendance(db, student_id, session_id, latitude, longitude)
