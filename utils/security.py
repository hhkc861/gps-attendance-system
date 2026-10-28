import os
from hashlib import sha256
from uuid import uuid4
from datetime import datetime, timedelta, timezone
from typing import Any

from argon2 import PasswordHasher
import jwt
from dotenv import load_dotenv

load_dotenv()

password_hasher = PasswordHasher()
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return password_hasher.verify(hashed_password, plain_password)
    except:
        return False


def create_access_token(data: dict[str, Any]) -> str:
    secret = os.getenv("JWT_SECRET")
    if not secret or len(secret) < 32:
        raise RuntimeError("JWT_SECRET must contain at least 32 characters")

    payload = data.copy()
    payload["jti"] = str(uuid4())
    payload["exp"] = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    return jwt.encode(payload, secret, algorithm="HS256")


def token_digest(token: str) -> str:
    return sha256(token.encode("utf-8")).hexdigest()


def decode_access_token(token: str) -> dict[str, Any]:
    secret = os.getenv("JWT_SECRET")
    if not secret or len(secret) < 32:
        raise RuntimeError("JWT_SECRET must contain at least 32 characters")

    return jwt.decode(
        token,
        secret,
        algorithms=["HS256"],
        options={"require": ["exp", "sub"]},
    )
