from typing import Any, Optional

from sqlalchemy import or_, select

from database import get_session
from models import User
from utils.security import hash_password


def _serialize_user(user: User) -> dict[str, Any]:
    return {
        "id": str(user.id),
        "code": user.code,
        "fullName": user.full_name,
        "email": user.email,
        "role": user.role,
        "createdAt": user.created_at,
    }


def create_user(payload: dict[str, Any]) -> dict[str, Any]:
    for field in ("code", "fullName", "email", "password"):
        if not payload.get(field):
            raise ValueError(f"{field} is required")

    user = User(
        code=payload["code"],
        full_name=payload["fullName"],
        email=payload["email"].lower(),
        password_hash=hash_password(payload["password"]),
        role=payload.get("role", "STUDENT"),
    )
    with get_session() as session:
        session.add(user)
        session.commit()
        session.refresh(user)
        return _serialize_user(user)


def list_users(
    role: Optional[str] = None,
    search: Optional[str] = None,
    page_size: int = 100,
    page_number: int = 1,
) -> list[dict[str, Any]]:
    statement = select(User)
    if role:
        statement = statement.where(User.role == role)
    if search:
        pattern = f"%{search}%"
        statement = statement.where(
            or_(
                User.code.ilike(pattern),
                User.full_name.ilike(pattern),
                User.email.ilike(pattern),
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
