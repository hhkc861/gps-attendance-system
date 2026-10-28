import pytest
from fastapi.testclient import TestClient
from httpx import Headers

from schemas.auth_schema import LoginRequest, LoginResponse, LogoutResponse

AUTH_URL = "/api/auth"


def test_login_success(client: TestClient):
    login_req = LoginRequest(username="admin", password="admin")
    response = client.post(f"{AUTH_URL}/login", json=login_req.model_dump(mode="json"))

    assert response.status_code == 200
    data = LoginResponse.model_validate(response.json())
    assert data.success is True
    assert data.data.tokenType == "Bearer"
    assert len(data.data.accessToken) > 20
    assert data.data.user.username == "admin"


def test_login_wrong_password(client: TestClient):
    login_req = LoginRequest(username="admin", password="IncorrectPassword123!")
    response = client.post(f"{AUTH_URL}/login", json=login_req.model_dump(mode="json"))

    assert response.status_code == 401


def test_login_non_existent_user(client: TestClient):
    login_req = LoginRequest(username="ghost_user_not_exist", password="Password123!")
    response = client.post(f"{AUTH_URL}/login", json=login_req.model_dump(mode="json"))

    assert response.status_code == 401


@pytest.mark.parametrize("blank_password", ["", "   ", "\t\n"])
def test_login_blank_password(client: TestClient, blank_password: str):
    login_req = LoginRequest.model_construct(username="admin", password=blank_password)
    response = client.post(f"{AUTH_URL}/login", json=login_req.model_dump(mode="json"))

    assert response.status_code == 422


def test_access_protected_route_without_token(client: TestClient):
    res = client.post(f"{AUTH_URL}/logout")
    assert res.status_code == 401


def test_access_protected_route_with_invalid_token(client: TestClient):
    headers = Headers({"Authorization": "Bearer invalid_malformed_token_12345"})
    res = client.post(f"{AUTH_URL}/logout", headers=headers)
    assert res.status_code == 401


def test_logout_session_and_token_revocation(client: TestClient):

    login_req = LoginRequest(username="admin", password="admin")
    login_res = client.post(f"{AUTH_URL}/login", json=login_req.model_dump(mode="json"))
    token = LoginResponse.model_validate(login_res.json()).data.accessToken

    headers = Headers()
    headers["Authorization"] = f"Bearer {token}"

    logout_res = client.post(f"{AUTH_URL}/logout", headers=headers)
    assert logout_res.status_code == 200
    logout_data = LogoutResponse.model_validate(logout_res.json())
    assert logout_data.success is True

    revoked_check = client.post(f"{AUTH_URL}/logout", headers=headers)
    assert revoked_check.status_code == 401
