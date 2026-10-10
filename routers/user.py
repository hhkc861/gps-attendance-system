from fastapi import APIRouter
from services.user_service import create_user_db, get_users_db, delete_user_db

router = APIRouter(prefix="/api/users", tags=["Users"])

@router.post("", status_code=201)
def create_user(user_request: dict):
    created = create_user_db(user_request)
    return {"success": True, "message": "Tạo tài khoản thành công", "data": created}

@router.get("")
def get_users(role: str = None, search: str = None, page_size: int = 10, page_number: int = 1):
    users = get_users_db(role, search, page_size, page_number)
    return {"success": True, "data": users}

@router.delete("/{id}")
def delete_user(id: str):
    delete_user_db(id)
    return {"success": True, "message": "Xóa tài khoản thành công"}