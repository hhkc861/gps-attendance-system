from datetime import timezone
from haversine import Unit, haversine
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from database import get_session
from models import AttendanceRecord, AttendanceSession, Section, now_utc
from schemas.session_schema import CheckInResponse


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

        if start_time.tzinfo is not None:
            start_time = start_time.astimezone(timezone.utc).replace(tzinfo=None)
        if end_time.tzinfo is not None:
            end_time = end_time.astimezone(timezone.utc).replace(tzinfo=None)

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

        now = now_utc()
        if now < session.start_time or now > session.end_time:
            raise ValueError("Session is not currently active")

        section = db.scalar(
            select(Section)
            .options(selectinload(Section.students))
            .where(Section.id == session.section_id)
        )
        if not section or student_id not in {s.id for s in section.students}:
            raise PermissionError("The student is not enrolled in this class section")

        existing_record = db.scalar(
            select(AttendanceRecord).where(
                AttendanceRecord.session_id == session_id,
                AttendanceRecord.student_id == student_id,
            )
        )
        if existing_record:
            raise FileExistsError("Student has already checked in for this session")

        center = (session.center_lat, session.center_lng)
        distance = round(haversine(center, (lat, lng), unit=Unit.METERS), 2)

        status = (
            "PRESENT" if distance <= session.radius_meters else "REJECTED_OUT_OF_RANGE"
        )

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

        message = (
            "Check-in successful (within range)"
            if status == "PRESENT"
            else "Check-in rejected (out of range)"
        )

        return CheckInResponse(
            recordId=record.id,
            sessionId=session_id,
            studentId=student_id,
            distanceMeters=distance,
            status=status,
            checkedInAt=record.checked_in_at,
            message=message,
        )
