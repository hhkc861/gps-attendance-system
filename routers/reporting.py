from fastapi import APIRouter
from services.reporting_service import get_student_attendance_history, override_attendance_status

router = APIRouter(prefix="/api", tags=["Reporting"])

@router.get("/students/me/attendance-records")
def my_attendance():
    data = get_student_attendance_history("uuid-student-id")
    return {"success": True, "data": data}

@router.patch("/sessions/{id}/records/{studentId}")
def override_record(id: str, studentId: str, req: dict):
    data = override_attendance_status(id, studentId, req.get("status"), req.get("overrideReason"))
    return {"success": True, "message": "Cập nhật trạng thái thành công", "data": data}