from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from database import get_session
from services.reporting_service import get_section_attendance_report

router = APIRouter(prefix="/api/reports", tags=["Reporting"])

@router.get("/sections/{section_id}", status_code=status.HTTP_200_OK)
def get_report_by_section(section_id: int, db: Session = Depends(get_session)):

    return get_section_attendance_report(db, section_id)
