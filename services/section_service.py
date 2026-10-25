from typing import Any

from sqlalchemy import select

from database import get_session
from models import Section, User

from schemas.section_schema import SectionCreateRequest, SectionCreateResponse


def create_section(request: SectionCreateRequest) -> SectionCreateResponse:
    section_code = request.sectionCode.strip()
    teacher_usernames = request.teachers
    student_usernames = request.students

    with get_session() as session:
        requested_usernames = set(teacher_usernames + student_usernames)
        users = session.scalars(
            select(User).where(User.username.in_(requested_usernames))
        ).all()
        users_by_username = {user.username: user for user in users}
        if len(users_by_username) != len(requested_usernames):
            raise LookupError("One or more accounts could not be found")

        section = Section(
            section_code=section_code,
            teachers=[users_by_username[username] for username in teacher_usernames],
            students=[users_by_username[username] for username in student_usernames],
        )

        session.add(section)
        session.commit()
        session.refresh(section)

        return SectionCreateResponse(
            sectionId=section.id,
            sectionCode=section.section_code,
            teachers=teacher_usernames,
            students=student_usernames,
            createdAt=section.created_at,
        )
