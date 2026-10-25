from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from services.user_service import (
    create_user as create_user_service,
    delete_user as delete_user_service,
    list_users,
)

router = APIRouter(prefix="/api/users", tags=["Users"])

@router.post("", status_code=201)
def create_user(user_request: dict):
    try:
        created = create_user_service(user_request)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except IntegrityError as error:
        raise HTTPException(
            status_code=409, detail="Username or email already exists"
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