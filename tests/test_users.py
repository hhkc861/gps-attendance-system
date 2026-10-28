import uuid
import pytest
from fastapi.testclient import TestClient
from httpx import Headers

from schemas.user_schema import (
    UserCreateRequest,
    UserDeleteResponse,
    UserListResponse,
    UserResponse,
    UserRole,
)

USERS_URL = "/api/users"


@pytest.mark.parametrize("role", ["STUDENT", "TEACHER", "ADMIN"])
def test_admin_can_create_user(
    client: TestClient,
    admin_headers: Headers,
    role: UserRole,
):
    username = f"user_{role.lower()}_{uuid.uuid4().hex[:6]}"
    create_req = UserCreateRequest(
        username=username,
        fullName=f"Full Name {role}",
        password="ValidPassword123!",
        role=role,
    )
    response = client.post(
        USERS_URL,
        json=create_req.model_dump(mode="json"),
        headers=admin_headers,
    )
    assert response.status_code == 201

    data = UserResponse.model_validate(response.json())
    assert data.username == username
    assert data.role == role
    assert data.id > 0


def test_create_user_duplicate_username(client: TestClient, admin_headers: Headers):
    username = f"dup_{uuid.uuid4().hex[:6]}"
    create_req = UserCreateRequest(
        username=username,
        fullName="Duplicated User",
        password="ValidPassword123!",
        role="STUDENT",
    )
    res1 = client.post(
        USERS_URL,
        json=create_req.model_dump(mode="json"),
        headers=admin_headers,
    )
    assert res1.status_code == 201

    res2 = client.post(
        USERS_URL,
        json=create_req.model_dump(mode="json"),
        headers=admin_headers,
    )
    assert res2.status_code == 409


@pytest.mark.parametrize("fixture_name", ["teacher_headers", "student_headers"])
def test_non_admin_cannot_create_user(client: TestClient, request, fixture_name: str):
    auth_headers: Headers = request.getfixturevalue(fixture_name)
    create_req = UserCreateRequest(
        username=f"hack_{uuid.uuid4().hex[:6]}",
        fullName="Unauthorized Attempt",
        password="ValidPassword123!",
        role="STUDENT",
    )
    response = client.post(
        USERS_URL,
        json=create_req.model_dump(mode="json"),
        headers=auth_headers,
    )
    assert response.status_code == 403


def test_delete_user_lifecycle(client: TestClient, admin_headers: Headers):
    create_req = UserCreateRequest(
        username=f"del_{uuid.uuid4().hex[:6]}",
        fullName="User To Delete",
        password="ValidPassword123!",
        role="STUDENT",
    )
    create_res = client.post(
        USERS_URL,
        json=create_req.model_dump(mode="json"),
        headers=admin_headers,
    )
    user = UserResponse.model_validate(create_res.json())

    del_res = client.delete(f"{USERS_URL}/{user.id}", headers=admin_headers)
    assert del_res.status_code == 200

    del_data = UserDeleteResponse.model_validate(del_res.json())
    assert del_data.success is True


def test_list_users_filters(client: TestClient, admin_headers: Headers):
    response = client.get(
        f"{USERS_URL}?role=STUDENT&page_size=10",
        headers=admin_headers,
    )
    assert response.status_code == 200

    data = UserListResponse.model_validate(response.json())
    assert all(u.role == "STUDENT" for u in data.users)


def test_delete_user_not_found(client: TestClient, admin_headers: Headers):
    res = client.delete(f"{USERS_URL}/999999", headers=admin_headers)
    assert res.status_code == 404


def test_non_admin_cannot_delete_user(
    client: TestClient,
    student_headers: Headers,
    test_student_2: UserResponse,
):
    res = client.delete(f"{USERS_URL}/{test_student_2.id}", headers=student_headers)
    assert res.status_code == 403
