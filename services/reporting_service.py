def get_student_attendance_history(student_id: str):
    # UC10: Lịch sử điểm danh cá nhân[cite: 1]
    return [{"recordId": "uuid-record-id", "sessionName": "Buổi học ngày 21/09/2026", "status": "PRESENT"}]

def override_attendance_status(session_id: str, student_id: str, status_val: str, reason: str):
    # UC12.2: Sửa trạng thái điểm danh thủ công[cite: 1]
    return {"sessionId": session_id, "studentId": student_id, "status": status_val, "overrideReason": reason}