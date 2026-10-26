from haversine import Unit, haversine
from sqlalchemy import select
from database import get_session
from models import AttendanceRecord, AttendanceSession, Section, now_utc


def open_session(
    section_id: int,
    center_lat: float,
    center_lng: float,
    radius: float,
    start_time,
    end_time,
):
    with get_session() as db:
        section = db.get(Section, section_id)
        if not section:
            raise LookupError("Class section not found")

        session = AttendanceSession(
            section_id=section_id,
            center_lat=center_lat,
            center_lng=center_lng,
            radius_meters=radius,
            start_time=start_time,
            end_time=end_time,
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session


def process_checkin(session_id: int, student_id: int, lat: float, lng: float):
    with get_session() as db:
        session = db.get(AttendanceSession, session_id)
        if not session:
            raise LookupError("Session not found")

        # Tính khoảng cách GPS theo Haversine
        center = (session.center_lat, session.center_lng)
        distance = round(haversine(center, (lat, lng), unit=Unit.METERS), 2)

        status = "PRESENT" if distance <= session.radius_meters else "REJECTED_OUT_OF_RANGE"
        now = now_utc()

        # Tìm xem sinh viên đã có bản ghi chưa để tránh lỗi dính UniqueConstraint sập 500
        record = db.scalar(
            select(AttendanceRecord).where(
                AttendanceRecord.session_id == session_id,
                AttendanceRecord.student_id == student_id,
            )
        )

        if record:
            record.lat = lat
            record.lng = lng
            record.distance_meters = distance
            record.status = status
            record.checked_in_at = now
        else:
            record = AttendanceRecord(
                session_id=session_id,
                student_id=student_id,
                lat=lat,
                lng=lng,
                distance_meters=distance,
                status=status,
                checked_in_at=now,
            )
            db.add(record)

        db.commit()
        db.refresh(record)

        return {
            "recordId": record.id,
            "sessionId": session_id,
            "studentId": student_id,
            "distanceMeters": distance,
            "status": status,
            "checkedInAt": record.checked_in_at,
            "message": "Check-in processed successfully",
        }
