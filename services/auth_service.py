from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone

from database import get_session
from models import RevokedToken, User
from schemas.auth_schema import LoginData, LoginRequest
from schemas.user_schema import UserResponse
from utils.security import (
    ACCESS_TOKEN_EXPIRE_SECONDS,
    create_access_token,
    verify_password,
    decode_access_token,
    token_digest,
)


class InvalidCredentialsError(ValueError):
    pass


def logout_user(token: str) -> None:
    payload = decode_access_token(token)
    digest = token_digest(token)
    with get_session() as session:
        session.add(
            RevokedToken(
                token_hash=digest,
                expires_at=datetime.fromtimestamp(payload["exp"], timezone.utc).replace(
                    tzinfo=None
                ),
            )
        )
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            # Concurrent logout requests may revoke the same token.
            if session.get(RevokedToken, digest) is None:
                raise


def authenticate_user(login_data: LoginRequest) -> LoginData:
    with get_session() as session:
        user = session.scalar(select(User).where(User.username == login_data.username))
        if user is None:
            raise InvalidCredentialsError("Username does not exist")

        is_match = verify_password(login_data.password, user.password_hash)
        if not is_match:
            raise InvalidCredentialsError("Invalid username or password")

        return LoginData(
            accessToken=create_access_token(sub=str(user.id)),
            expiresIn=ACCESS_TOKEN_EXPIRE_SECONDS,
            user=UserResponse(
                id=user.id,
                username=user.username,
                fullName=user.full_name,
                role=user.role,
                createdAt=user.created_at,
            ),
        )
