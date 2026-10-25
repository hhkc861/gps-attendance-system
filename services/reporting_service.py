def get_student_attendance_history(student_id: str):
    # UC10: Personal attendance history
    return [
        {
            "recordId": "uuid-record-id",
            "sessionName": "Class session on 2026-09-21",
            "status": "PRESENT",
        }
    ]


def override_attendance_status(
    session_id: str, student_id: str, status_val: str, reason: str
):
    # UC12.2: Manually update an attendance status
    return {
        "sessionId": session_id,
        "studentId": student_id,
        "status": status_val,
        "overrideReason": reason,
    }
