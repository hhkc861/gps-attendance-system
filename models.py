from datetime import datetime, timezone
from typing import Literal, Optional

from sqlalchemy import Boolean, CheckConstraint, Column, DateTime, Float, ForeignKey
from sqlalchemy import Integer, String, Table, UniqueConstraint
from sqlalchemy.orm import (
    Mapped,
    declarative_base,
    mapped_column,
    relationship,
)

from schemas.session_schema import AttendanceStatus
from schemas.user_schema import UserRole


def now_utc() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


Base = declarative_base()


section_teachers = Table(
    "section_teachers",
    Base.metadata,
    Column("section_id", ForeignKey("sections.id"), primary_key=True),
    Column("teacher_user_id", ForeignKey("users.id"), primary_key=True),
)


section_students = Table(
    "section_students",
    Base.metadata,
    Column("section_id", ForeignKey("sections.id"), primary_key=True),
    Column("student_user_id", ForeignKey("users.id"), primary_key=True),
)


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint(
            "role IN ('ADMIN', 'TEACHER', 'STUDENT')",
            name="ck_users_role",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        String(20), nullable=False, default="STUDENT"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(),
        nullable=False,
        default=now_utc,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(),
        nullable=False,
        default=now_utc,
        onupdate=now_utc,
    )


class Section(Base):
    __tablename__ = "sections"
    __table_args__ = (
        UniqueConstraint(
            "section_code",
            name="uq_sections_section_code",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    section_code: Mapped[str] = mapped_column(String(100), nullable=False)
    teachers: Mapped[list[User]] = relationship(
        secondary=section_teachers,
    )
    students: Mapped[list[User]] = relationship(
        secondary=section_students,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(),
        nullable=False,
        default=now_utc,
    )


class Enrollment(Base):
    __tablename__ = "enrollments"

    student_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    section_id: Mapped[int] = mapped_column(ForeignKey("sections.id"), primary_key=True)
    enrolled_at: Mapped[datetime] = mapped_column(
        DateTime(),
        nullable=False,
        default=now_utc,
    )


class AttendanceSession(Base):
    __tablename__ = "attendance_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    section_id: Mapped[int] = mapped_column(ForeignKey("sections.id"), nullable=False)
    center_lat: Mapped[float] = mapped_column(Float, nullable=False)
    center_lng: Mapped[float] = mapped_column(Float, nullable=False)
    radius_meters: Mapped[float] = mapped_column(Float, nullable=False)
    start_time: Mapped[datetime] = mapped_column(DateTime(), nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime(), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(),
        nullable=False,
        default=now_utc,
    )


class AttendanceRecord(Base):
    __tablename__ = "attendance_records"
    __table_args__ = (
        UniqueConstraint(
            "session_id", "student_id", name="uq_attendance_session_student"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[int] = mapped_column(
        ForeignKey("attendance_sessions.id"), nullable=False
    )
    student_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    lat: Mapped[float] = mapped_column(Float, nullable=False)
    lng: Mapped[float] = mapped_column(Float, nullable=False)
    distance_meters: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[AttendanceStatus] = mapped_column(String(30), nullable=False)
    checked_in_at: Mapped[datetime] = mapped_column(
        DateTime(),
        nullable=False,
        default=now_utc,
    )
    is_manually_overridden: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    override_reason: Mapped[Optional[str]] = mapped_column(String(500))
