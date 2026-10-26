from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from schemas.user_schema import UserCreateRequest, UserCreateResponse
from utils.auth import require_admin
from services.user_service import (
    create_user as create_user_service,
    delete_user as delete_user_service,
    list_users,
)

router = APIRouter(prefix="/api/users", tags=["Users"])

@router.post(
    "",
    status_code=201,
    response_model=UserCreateResponse,
    dependencies=[Depends(require_admin)],
    summary="Create an account",
)
def create_user(user_request: UserCreateRequest):
    try:
        created = create_user_service(user_request)
    except IntegrityError as error:
        if getattr(error.orig, "sqlstate", None) != "23505":
            raise
        raise HTTPException(
            status_code=409, detail="Username already exists"
        ) from error
    return {"success": True, "message": "Account created successfully", "data": created}

@router.get("")
def get_users(
    role: Optional[str] = None,
    search: Optional[str] = None,
    page_size: int = Query(default=10, ge=1, le=100),
    page_number: int = Query(default=1, ge=1),
):
    users = list_users(
        role=role,
        search=search,
        page_size=page_size,
        page_number=page_number,
    )
    return {"success": True, "data": users}

@router.delete("/{id}")
def delete_user(id: str):
    if not delete_user_service(id):
        raise HTTPException(status_code=404, detail="Account not found")
    return {"success": True, "message": "Account deleted successfully"}
