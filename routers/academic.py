from fastapi import APIRouter
from services.academic_service import (
    create_class_db,
    assign_lecturer_db,
    add_student_to_class_db,
)

router = APIRouter(prefix="/api/classes", tags=["Academic & Classes"])


@router.post("", status_code=201)
def create_class(req: dict):
    return {
        "success": True,
        "message": "Tạo lớp học phần thành công",
        "data": create_class_db(req),
    }


@router.put("/{id}/lecturer")
def assign_lecturer(id: str, req: dict):
    return {
        "success": True,
        "message": "Phân công giảng viên thành công",
        "data": assign_lecturer_db(id, req.get("lecturerUserId")),
    }


@router.post("/{id}/students", status_code=201)
def add_student(id: str, req: dict):
    return {
        "success": True,
        "message": "Thêm sinh viên thành công",
        "data": add_student_to_class_db(id, req.get("studentId")),
    }
