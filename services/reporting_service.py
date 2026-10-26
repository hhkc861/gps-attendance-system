from sqlalchemy.orm import Session
from sqlalchemy import select
from models import AttendanceSession, AttendanceRecord, User

def get_section_attendance_report(db: Session, section_id: int):

    sessions = db.scalars(
        select(AttendanceSession).where(AttendanceSession.section_id == section_id)
    ).all()

    total_sessions = len(sessions)
    session_ids = [s.id for s in sessions]

    if total_sessions == 0:
        return {
            "sectionId": section_id,
            "totalSessions": 0,
            "reportData": []
        }

    records = db.scalars(
        select(AttendanceRecord).where(AttendanceRecord.session_id.in_(session_ids))
    ).all()

    return {
        "sectionId": section_id,
        "totalSessions": total_sessions,
        "reportData": [
            {
                "recordCount": len(records),
                "note": "Successfully connected to real data from AttendanceRecord table."
            }
        ]
    }
