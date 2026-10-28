import uuid
from fastapi.testclient import TestClient
from httpx import Headers

from schemas.section_schema import SectionCreateRequest, SectionCreateResponse
from schemas.user_schema import UserResponse

SECTIONS_URL = "/api/sections"


def test_create_section_success(
    client: TestClient,
    admin_headers: Headers,
    test_teacher: UserResponse,
    test_student_1: UserResponse,
):
    section_code = f"SEC_VALID_{uuid.uuid4().hex[:8].upper()}"
    create_req = SectionCreateRequest(
        sectionCode=section_code,
        teachers=[test_teacher.username],
        students=[test_student_1.username],
    )
    response = client.post(
        SECTIONS_URL,
        json=create_req.model_dump(mode="json"),
        headers=admin_headers,
    )
    assert response.status_code == 201

    data = SectionCreateResponse.model_validate(response.json())
    assert data.sectionCode == section_code
    assert test_teacher.username in data.teachers
    assert test_student_1.username in data.students


def test_create_section_user_both_roles(
    client: TestClient,
    admin_headers: Headers,
    test_teacher: UserResponse,
):
    conflict_req = SectionCreateRequest.model_construct(
        sectionCode=f"SEC_CONFLICT_{uuid.uuid4().hex[:4]}",
        teachers=[test_teacher.username],
        students=[test_teacher.username],
    )
    response = client.post(
        SECTIONS_URL,
        json=conflict_req.model_dump(mode="json"),
        headers=admin_headers,
    )
    assert response.status_code in (400, 422)


def test_create_section_user_not_found(client: TestClient, admin_headers: Headers):
    not_found_req = SectionCreateRequest(
        sectionCode=f"SEC_GHOST_{uuid.uuid4().hex[:8]}",
        teachers=["non_existent_teacher_9999"],
        students=[],
    )
    response = client.post(
        SECTIONS_URL,
        json=not_found_req.model_dump(mode="json"),
        headers=admin_headers,
    )
    assert response.status_code == 404


def test_create_section_forbidden_for_teacher(
    client: TestClient,
    teacher_headers: Headers,
    test_teacher: UserResponse,
):
    forbidden_req = SectionCreateRequest(
        sectionCode=f"SEC_TEACH_{uuid.uuid4().hex[:8]}",
        teachers=[test_teacher.username],
        students=[],
    )
    response = client.post(
        SECTIONS_URL,
        json=forbidden_req.model_dump(mode="json"),
        headers=teacher_headers,
    )
    assert response.status_code == 403


def test_create_section_forbidden_for_student(
    client: TestClient,
    student_headers: Headers,
    test_teacher: UserResponse,
):
    req = SectionCreateRequest(
        sectionCode="SEC_STD_HACK",
        teachers=[test_teacher.username],
        students=[],
    )
    res = client.post(
        SECTIONS_URL, json=req.model_dump(mode="json"), headers=student_headers
    )
    assert res.status_code == 403


def test_create_section_duplicate_code(
    client: TestClient,
    admin_headers: Headers,
    test_teacher: UserResponse,
):
    code = f"SEC_DUP_{uuid.uuid4().hex[:6].upper()}"
    req = SectionCreateRequest(
        sectionCode=code, teachers=[test_teacher.username], students=[]
    )
    res1 = client.post(
        SECTIONS_URL, json=req.model_dump(mode="json"), headers=admin_headers
    )
    assert res1.status_code == 201

    res2 = client.post(
        SECTIONS_URL, json=req.model_dump(mode="json"), headers=admin_headers
    )
    assert res2.status_code in (400, 409)
