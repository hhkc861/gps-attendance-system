from typing import cast
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from database import get_session
from models import AttendanceRecord, AttendanceSession, Section, User
from schemas.reporting_schema import (
    AttendanceStatus,
    SectionReportResponse,
    SessionReportResponse,
    SessionStudentAttendanceItem,
    StudentHistoryItem,
    StudentReportResponse,
    StudentSectionSummaryItem,
)


def get_session_report(session_id: int) -> SessionReportResponse:
    with get_session() as db:
        session = db.get(AttendanceSession, session_id)
        if not session:
            raise LookupError(f"Attendance session {session_id} not found")

        section = db.scalar(
            select(Section)
            .options(selectinload(Section.students))
            .where(Section.id == session.section_id)
        )
        if not section:
            raise LookupError(f"Section for session {session_id} not found")

        records = db.scalars(
            select(AttendanceRecord).where(AttendanceRecord.session_id == session_id)
        ).all()
        records_map = {r.student_id: r for r in records}

        student_items: list[SessionStudentAttendanceItem] = []
        present_cnt = 0
        rejected_cnt = 0
        absent_cnt = 0
        excused_cnt = 0

        sorted_students = sorted(section.students, key=lambda s: s.id)

        for student in sorted_students:
            rec = records_map.get(student.id)
            if rec:
                if rec.status == "PRESENT":
                    present_cnt += 1
                elif rec.status == "REJECTED_OUT_OF_RANGE":
                    rejected_cnt += 1
                elif rec.status == "EXCUSED":
                    excused_cnt += 1
                elif rec.status == "ABSENT":
                    absent_cnt += 1

                student_items.append(
                    SessionStudentAttendanceItem(
                        studentId=student.id,
                        username=student.username,
                        fullName=student.full_name,
                        status=cast(AttendanceStatus, rec.status),
                        lat=rec.lat,
                        lng=rec.lng,
                        distanceMeters=rec.distance_meters,
                        checkedInAt=rec.checked_in_at,
                        isManuallyOverridden=rec.is_manually_overridden,
                        overrideReason=rec.override_reason,
                    )
                )
            else:
                absent_cnt += 1
                student_items.append(
                    SessionStudentAttendanceItem(
                        studentId=student.id,
                        username=student.username,
                        fullName=student.full_name,
                        status="ABSENT",
                        lat=None,
                        lng=None,
                        distanceMeters=None,
                        checkedInAt=None,
                        isManuallyOverridden=False,
                        overrideReason=None,
                    )
                )

        total_enrolled = len(sorted_students)
        rate = (
            round((present_cnt / total_enrolled * 100), 2)
            if total_enrolled > 0
            else 0.0
        )

        return SessionReportResponse(
            sessionId=session.id,
            sectionId=section.id,
            sectionCode=section.section_code,
            centerLat=session.center_lat,
            centerLng=session.center_lng,
            radiusMeters=session.radius_meters,
            startTime=session.start_time,
            endTime=session.end_time,
            totalEnrolled=total_enrolled,
            presentCount=present_cnt,
            rejectedCount=rejected_cnt,
            absentCount=absent_cnt,
            excusedCount=excused_cnt,
            attendanceRate=rate,
            records=student_items,
        )


def get_section_report(section_id: int) -> SectionReportResponse:
    with get_session() as db:
        section = db.scalar(
            select(Section)
            .options(selectinload(Section.students))
            .where(Section.id == section_id)
        )
        if not section:
            raise LookupError(f"Class section {section_id} not found")

        sessions = db.scalars(
            select(AttendanceSession).where(AttendanceSession.section_id == section_id)
        ).all()
        session_ids = [s.id for s in sessions]
        total_sessions = len(sessions)

        records = []
        if session_ids:
            records = db.scalars(
                select(AttendanceRecord).where(
                    AttendanceRecord.session_id.in_(session_ids)
                )
            ).all()

        student_records = {s.id: [] for s in section.students}
        for r in records:
            if r.student_id in student_records:
                student_records[r.student_id].append(r)

        student_summaries: list[StudentSectionSummaryItem] = []
        total_present = 0
        sorted_students = sorted(section.students, key=lambda s: s.id)

        for student in sorted_students:
            recs = student_records[student.id]
            p_cnt = sum(1 for r in recs if r.status == "PRESENT")
            r_cnt = sum(1 for r in recs if r.status == "REJECTED_OUT_OF_RANGE")
            e_cnt = sum(1 for r in recs if r.status == "EXCUSED")

            recorded_session_ids = {r.session_id for r in recs}
            not_attended_count = total_sessions - len(recorded_session_ids)
            a_cnt = not_attended_count + sum(1 for r in recs if r.status == "ABSENT")

            rate = (
                round((p_cnt / total_sessions * 100), 2) if total_sessions > 0 else 0.0
            )
            total_present += p_cnt

            student_summaries.append(
                StudentSectionSummaryItem(
                    studentId=student.id,
                    username=student.username,
                    fullName=student.full_name,
                    totalSessions=total_sessions,
                    presentCount=p_cnt,
                    absentCount=a_cnt,
                    rejectedCount=r_cnt,
                    excusedCount=e_cnt,
                    attendanceRate=rate,
                )
            )

        total_possible = total_sessions * len(sorted_students)
        overall_rate = (
            round((total_present / total_possible * 100), 2)
            if total_possible > 0
            else 0.0
        )

        return SectionReportResponse(
            sectionId=section.id,
            sectionCode=section.section_code,
            totalSessions=total_sessions,
            totalStudents=len(sorted_students),
            overallAttendanceRate=overall_rate,
            students=student_summaries,
        )


def get_student_report(student_id: int) -> StudentReportResponse:
    with get_session() as db:
        student = db.get(User, student_id)
        if not student:
            raise LookupError(f"Student {student_id} not found")

        records = db.scalars(
            select(AttendanceRecord).where(AttendanceRecord.student_id == student_id)
        ).all()

        history: list[StudentHistoryItem] = []
        attended_count = 0

        for r in records:
            session = db.get(AttendanceSession, r.session_id)
            section = db.get(Section, session.section_id) if session else None
            if r.status == "PRESENT":
                attended_count += 1

            history.append(
                StudentHistoryItem(
                    sessionId=r.session_id,
                    sectionCode=section.section_code if section else "N/A",
                    sessionTime=session.start_time if session else r.checked_in_at,
                    status=cast(AttendanceStatus, r.status),
                    distanceMeters=r.distance_meters,
                    checkedInAt=r.checked_in_at,
                    isManuallyOverridden=r.is_manually_overridden,
                )
            )

        total = len(history)
        rate = round((attended_count / total * 100), 2) if total > 0 else 0.0

        return StudentReportResponse(
            studentId=student.id,
            username=student.username,
            fullName=student.full_name,
            totalSessions=total,
            attendedSessions=attended_count,
            attendanceRate=rate,
            history=history,
        )
