def create_class_db(request: dict):
    # UC4.3: Tạo lớp học phần
    return {"classId": "uuid-class-id", **request}


def assign_lecturer_db(class_id: str, lecturer_id: str):
    # UC5: Phân công giảng viên
    return {"classId": class_id, "lecturerUserId": lecturer_id}


def add_student_to_class_db(class_id: str, student_id: str):
    # UC6.1: Thêm sinh viên vào lớp
    return {"classId": class_id, "studentId": student_id}
