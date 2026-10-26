from typing import Optional

from sqlalchemy import or_, select

from database import get_session
from models import User
from schemas.user_schema import UserCreateRequest, UserResponse, UserRole
from utils.security import hash_password


def _serialize_user(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        username=user.username,
        fullName=user.full_name,
        role=user.role,
        createdAt=user.created_at,
    )


def create_user(payload: UserCreateRequest) -> UserResponse:
    user = User(
        username=payload.username,
        full_name=payload.fullName,
        password_hash=hash_password(payload.password),
        role=payload.role,
    )
    with get_session() as session:
        session.add(user)
        session.commit()
        session.refresh(user)
        return _serialize_user(user)


def list_users(
    role: Optional[UserRole] = None,
    search: Optional[str] = None,
    page_size: int = 100,
    page_number: int = 1,
) -> list[UserResponse]:
    statement = select(User)
    if role:
        statement = statement.where(User.role == role)
    if search:
        pattern = f"%{search}%"
        statement = statement.where(
            or_(
                User.username.ilike(pattern),
                User.full_name.ilike(pattern),
            )
        )
    statement = statement.offset((page_number - 1) * page_size).limit(page_size)

    with get_session() as session:
        users = session.scalars(statement).all()
        return [_serialize_user(user) for user in users]


def delete_user(user_id: str) -> bool:
    try:
        user_id_number = int(user_id)
    except ValueError:
        return False
    with get_session() as session:
        user = session.get(User, user_id_number)
        if user is None:
            return False
        session.delete(user)
        session.commit()
        return True
