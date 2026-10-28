import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from httpx import Headers

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from main import app
from schemas.auth_schema import LoginRequest, LoginResponse
from schemas.section_schema import SectionCreateRequest, SectionCreateResponse
from schemas.session_schema import SessionCreateRequest, SessionResponse
from schemas.user_schema import UserCreateRequest, UserResponse

LOGIN_URL = "/api/auth/login"
USERS_URL = "/api/users"
SECTIONS_URL = "/api/sections"
SESSIONS_URL = "/api/sessions"


@pytest.fixture(scope="session")
def client() -> Generator[TestClient, None, None]:
    from database import connect_database

    connect_database()

    test_client = TestClient(app)
    yield test_client


def create_auth_headers(client: TestClient, username: str, password: str) -> Headers:
    login_req = LoginRequest(username=username, password=password)
    response = client.post(LOGIN_URL, json=login_req.model_dump(mode="json"))
    if response.status_code == 200:
        login_res = LoginResponse.model_validate(response.json())
        headers = Headers()
        headers["Authorization"] = f"Bearer {login_res.data.accessToken}"
        return headers
    raise RuntimeError(f"Authentication failed for user {username}: {response.text}")


@pytest.fixture(scope="session")
def admin_headers(client: TestClient) -> Headers:
    return create_auth_headers(client, username="admin", password="admin")


@pytest.fixture(scope="session")
def test_teacher(client: TestClient, admin_headers: Headers) -> UserResponse:
    username = f"teacher_{uuid.uuid4().hex[:8]}"
    create_req = UserCreateRequest(
        username=username,
        fullName="Test Faculty Teacher",
        password="TeacherPassword123!",
        role="TEACHER",
    )
    res = client.post(
        USERS_URL, json=create_req.model_dump(mode="json"), headers=admin_headers
    )
    assert res.status_code == 201
    return UserResponse.model_validate(res.json())


@pytest.fixture(scope="session")
def teacher_headers(client: TestClient, test_teacher: UserResponse) -> Headers:
    return create_auth_headers(
        client, username=test_teacher.username, password="TeacherPassword123!"
    )


@pytest.fixture(scope="session")
def test_student_1(client: TestClient, admin_headers: Headers) -> UserResponse:
    username = f"std1_{uuid.uuid4().hex[:8]}"
    create_req = UserCreateRequest(
        username=username,
        fullName="Nguyen Van Student One",
        password="StudentPassword123!",
        role="STUDENT",
    )
    res = client.post(
        USERS_URL, json=create_req.model_dump(mode="json"), headers=admin_headers
    )
    assert res.status_code == 201
    return UserResponse.model_validate(res.json())


@pytest.fixture(scope="session")
def student_headers(client: TestClient, test_student_1: UserResponse) -> Headers:
    return create_auth_headers(
        client, username=test_student_1.username, password="StudentPassword123!"
    )


@pytest.fixture(scope="session")
def test_student_2(client: TestClient, admin_headers: Headers) -> UserResponse:
    username = f"std2_{uuid.uuid4().hex[:8]}"
    create_req = UserCreateRequest(
        username=username,
        fullName="Tran Van Student Two",
        password="StudentPassword123!",
        role="STUDENT",
    )
    res = client.post(
        USERS_URL, json=create_req.model_dump(mode="json"), headers=admin_headers
    )
    assert res.status_code == 201
    return UserResponse.model_validate(res.json())


@pytest.fixture(scope="session")
def student2_headers(client: TestClient, test_student_2: UserResponse) -> Headers:
    return create_auth_headers(
        client, username=test_student_2.username, password="StudentPassword123!"
    )


@pytest.fixture(scope="session")
def unenrolled_student_headers(client: TestClient, admin_headers: Headers) -> Headers:
    username = f"stranger_{uuid.uuid4().hex[:8]}"
    create_req = UserCreateRequest(
        username=username,
        fullName="Stranger Student",
        password="StudentPassword123!",
        role="STUDENT",
    )
    res = client.post(
        USERS_URL, json=create_req.model_dump(mode="json"), headers=admin_headers
    )
    assert res.status_code == 201
    return create_auth_headers(
        client, username=username, password="StudentPassword123!"
    )


@pytest.fixture(scope="session")
def test_section(
    client: TestClient,
    admin_headers: Headers,
    test_teacher: UserResponse,
    test_student_1: UserResponse,
    test_student_2: UserResponse,
) -> SectionCreateResponse:
    section_code = f"SEC_{uuid.uuid4().hex[:8].upper()}"
    section_req = SectionCreateRequest(
        sectionCode=section_code,
        teachers=[test_teacher.username],
        students=[test_student_1.username, test_student_2.username],
    )
    response = client.post(
        SECTIONS_URL, json=section_req.model_dump(mode="json"), headers=admin_headers
    )
    assert response.status_code == 201
    return SectionCreateResponse.model_validate(response.json())


@pytest.fixture
def active_session(
    client: TestClient,
    teacher_headers: Headers,
    test_section: SectionCreateResponse,
) -> SessionResponse:
    now = datetime.now(timezone.utc)
    session_req = SessionCreateRequest(
        sectionId=test_section.sectionId,
        centerLat=21.03824,
        centerLng=105.78256,
        radiusMeters=50.0,
        startTime=now - timedelta(minutes=5),
        endTime=now + timedelta(minutes=25),
    )
    response = client.post(
        SESSIONS_URL, json=session_req.model_dump(mode="json"), headers=teacher_headers
    )
    assert response.status_code == 201
    return SessionResponse.model_validate(response.json())
