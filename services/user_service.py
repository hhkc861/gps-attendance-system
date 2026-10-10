def create_user_db(request: dict):
    # UC3.1: Tạo tài khoản mới[cite: 1]
    return {
        "id": "uuid-user-id",
        "code": request.get("code", "24021625"),
        "fullName": request.get("fullName", "Nguyễn Văn A"),
        "email": request.get("email"),
        "createdAt": "2026-09-21T10:00:00Z"
    }

def get_users_db(role: str, search: str, page_size: int, page_number: int):
    # UC3.2: Lấy danh sách tài khoản[cite: 1]
    return [{"id": "uuid-user-id", "code": "24021625", "fullName": "Nguyễn Văn A", "role": role or "STUDENT"}]

def delete_user_db(user_id: str):
    # UC3.3: Xóa tài khoản[cite: 1]
    return True