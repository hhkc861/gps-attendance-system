import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from models import Base

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://attendance:attendance@localhost:5432/gps_attendance",
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def connect_database() -> None:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    Base.metadata.create_all(bind=engine)


def close_database() -> None:
    engine.dispose()


def get_session() -> Session:
    return SessionLocal()
