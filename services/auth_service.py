from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone

from database import get_session
from models import RevokedToken, User
from schemas.auth_schema import LoginData, LoginRequest
from schemas.user_schema import UserResponse
from utils.security import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    hash_password,
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
        session.add(RevokedToken(
            token_hash=digest,
            expires_at=datetime.fromtimestamp(payload["exp"], timezone.utc).replace(tzinfo=None),
        ))
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            # Concurrent logout requests may revoke the same token.
            if session.get(RevokedToken, digest) is None:
                raise


# Perform password verification even if the username does not exist.
_DUMMY_PASSWORD_HASH = hash_password("unused-login-timing-placeholder")


def authenticate_user(login_data: LoginRequest) -> LoginData:
    with get_session() as session:
        user = session.scalar(select(User).where(User.username == login_data.username))
        password_hash = user.password_hash if user is not None else _DUMMY_PASSWORD_HASH
        password_valid = verify_password(login_data.password, password_hash)
        if user is None or not password_valid:
            raise InvalidCredentialsError("Invalid username or password")

        return LoginData(
            accessToken=create_access_token({"sub": str(user.id)}),
            expiresIn=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponse(
                id=user.id,
                username=user.username,
                fullName=user.full_name,
                role=user.role,
                createdAt=user.created_at,
            ),
        )
