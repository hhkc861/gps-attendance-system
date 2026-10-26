from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from psycopg.errors import ForeignKeyViolation, UniqueViolation
from schemas.user_schema import (
    UserCreateRequest,
    UserDeleteResponse,
    UserResponse,
    UserListResponse,
    UserRole,
)
from services.user_service import (
    create_user as create_user_service,
    delete_user as delete_user_service,
    list_users,
)
from sqlalchemy.exc import IntegrityError
from utils.auth import require_admin

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=UserResponse,
    dependencies=[Depends(require_admin)],
    summary="Create an account",
    description="Create a user account. Only an administrator can use this endpoint.\n\n"
    "If no role is supplied, the account is created as a student.",
    responses={
        status.HTTP_201_CREATED: {
            "description": "The account was created successfully."
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "A valid bearer token is required."
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "The authenticated user is not an administrator."
        },
        status.HTTP_409_CONFLICT: {"description": "The username is already in use."},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": "The request body is invalid."
        },
    },
)
def create_user(user_request: UserCreateRequest) -> UserResponse:
    try:
        return create_user_service(user_request)
    except IntegrityError as error:
        if isinstance(error.orig, UniqueViolation):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Username already exists"
            ) from error
        raise


@router.get(
    "",
    response_model=UserListResponse,
    summary="List user accounts",
    description="Return user accounts with optional role and text filters, plus pagination.",
    responses={
        status.HTTP_200_OK: {
            "description": "The matching accounts were returned successfully."
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": "A query parameter is outside its allowed range."
        },
    },
)
def get_users(
    role: Optional[UserRole] = Query(
        default=None,
        title="Role filter",
        description="Return only accounts with this role.",
        examples=["STUDENT"],
    ),
    search: Optional[str] = Query(
        default=None,
        title="Search term",
        description="Filter by a partial match in the username or full name.",
        examples=["24021400"],
    ),
    page_size: int = Query(
        default=10,
        ge=1,
        le=100,
        title="Page size",
        description="The maximum number of accounts to return (1–100).",
        examples=[10],
    ),
    page_number: int = Query(
        default=1,
        ge=1,
        title="Page number",
        description="The one-based page number to return.",
        examples=[1],
    ),
) -> UserListResponse:
    users = list_users(
        role=role,
        search=search,
        page_size=page_size,
        page_number=page_number,
    )
    return UserListResponse(users=users)


@router.delete(
    "/{id}",
    response_model=UserDeleteResponse,
    dependencies=[Depends(require_admin)],
    summary="Delete a user account",
    description="Permanently delete the account with the specified ID.\n\n"
    "Only an administrator can use this endpoint. Accounts referenced by existing "
    "records cannot be deleted.",
    responses={
        status.HTTP_200_OK: {"description": "The account was deleted successfully."},
        status.HTTP_401_UNAUTHORIZED: {
            "description": "A valid bearer token is required."
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "The authenticated user is not an administrator."
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "The account does not exist or the ID is invalid."
        },
        status.HTTP_409_CONFLICT: {
            "description": "The account is referenced by existing records."
        },
    },
)
def delete_user(
    id: str = Path(
        title="User ID",
        description="The ID of the account to delete.",
        examples=["12"],
    ),
) -> UserDeleteResponse:
    try:
        deleted = delete_user_service(id)
    except IntegrityError as error:
        if isinstance(error.orig, ForeignKeyViolation):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Account is referenced by existing records",
            ) from error
        raise

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Account not found"
        )

    return UserDeleteResponse(
        success=True,
        message="Account deleted successfully",
    )
