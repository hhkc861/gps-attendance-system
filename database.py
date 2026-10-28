import os
from contextlib import contextmanager
from typing import Generator
from dotenv import load_dotenv
from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import Session, sessionmaker

from models import Base, User
from utils.security import hash_password

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://attendance:attendance@127.0.0.1:5432/gps_attendance",
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_size=10, max_overflow=20)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def connect_database() -> None:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    Base.metadata.create_all(bind=engine)
    _create_bootstrap_admin()


def _create_bootstrap_admin() -> None:
    password = os.getenv("BOOTSTRAP_ADMIN_PASSWORD")
    if password is None:
        return
    if not password.strip():
        raise RuntimeError("BOOTSTRAP_ADMIN_PASSWORD must not be blank")

    with SessionLocal() as session:
        admin = session.scalar(select(User).where(User.username == "admin"))
        if admin is not None:
            return

        session.add(
            User(
                username="admin",
                full_name="Admin",
                password_hash=hash_password(password),
                role="ADMIN",
            )
        )
        session.commit()


def close_database() -> None:
    engine.dispose()


@contextmanager
def get_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
