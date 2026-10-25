from fastapi import APIRouter
from services.auth_service import authenticate_user, logout_user

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/login")
def login(login_request: dict):
    data = authenticate_user(login_request)
    return {"success": True, "message": "Login successful", "data": data}


@router.post("/logout")
def logout():
    logout_user()
    return {"success": True, "message": "Logout successful"}
