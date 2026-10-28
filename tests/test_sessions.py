from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
from httpx import Headers

from schemas.section_schema import SectionCreateResponse
from schemas.session_schema import (
    CheckInRequest,
    CheckInResponse,
    SessionCreateRequest,
    SessionResponse,
)

SESSIONS_URL = "/api/sessions"


def test_teacher_can_open_session(
    client: TestClient,
    teacher_headers: Headers,
    test_section: SectionCreateResponse,
):
    now = datetime.now(timezone.utc)
    session_req = SessionCreateRequest(
        sectionId=test_section.sectionId,
        centerLat=21.03824,
        centerLng=105.78256,
        radiusMeters=50.0,
        startTime=now,
        endTime=now + timedelta(minutes=45),
    )
    response = client.post(
        SESSIONS_URL,
        json=session_req.model_dump(mode="json"),
        headers=teacher_headers,
    )
    assert response.status_code == 201

    data = SessionResponse.model_validate(response.json())
    assert data.id > 0
    assert data.sectionId == test_section.sectionId


def test_student_cannot_open_session(
    client: TestClient,
    student_headers: Headers,
    test_section: SectionCreateResponse,
):
    now = datetime.now(timezone.utc)
    session_req = SessionCreateRequest(
        sectionId=test_section.sectionId,
        centerLat=21.03824,
        centerLng=105.78256,
        radiusMeters=50.0,
        startTime=now,
        endTime=now + timedelta(minutes=30),
    )
    response = client.post(
        SESSIONS_URL,
        json=session_req.model_dump(mode="json"),
        headers=student_headers,
    )
    assert response.status_code == 403


def test_open_session_invalid_time_window(
    client: TestClient,
    teacher_headers: Headers,
    test_section: SectionCreateResponse,
):
    now = datetime.now(timezone.utc)
    invalid_session_req = SessionCreateRequest.model_construct(
        sectionId=test_section.sectionId,
        centerLat=21.03824,
        centerLng=105.78256,
        radiusMeters=50.0,
        startTime=now + timedelta(minutes=30),
        endTime=now,
    )
    response = client.post(
        SESSIONS_URL,
        json=invalid_session_req.model_dump(mode="json"),
        headers=teacher_headers,
    )
    assert response.status_code == 422


def test_checkin_session_not_found(client: TestClient, student_headers: Headers):
    fake_session_id = 999999
    checkin_req = CheckInRequest(lat=21.03824, lng=105.78256)
    response = client.post(
        f"{SESSIONS_URL}/{fake_session_id}/check-in",
        json=checkin_req.model_dump(mode="json"),
        headers=student_headers,
    )
    assert response.status_code == 404


def test_checkin_expired_session(
    client: TestClient,
    teacher_headers: Headers,
    student_headers: Headers,
    test_section: SectionCreateResponse,
):
    now = datetime.now(timezone.utc)
    expired_req = SessionCreateRequest(
        sectionId=test_section.sectionId,
        centerLat=21.03824,
        centerLng=105.78256,
        radiusMeters=50.0,
        startTime=now - timedelta(minutes=60),
        endTime=now - timedelta(minutes=10),
    )
    create_res = client.post(
        SESSIONS_URL,
        json=expired_req.model_dump(mode="json"),
        headers=teacher_headers,
    )
    session_id = SessionResponse.model_validate(create_res.json()).id

    checkin_req = CheckInRequest(lat=21.03824, lng=105.78256)
    response = client.post(
        f"{SESSIONS_URL}/{session_id}/check-in",
        json=checkin_req.model_dump(mode="json"),
        headers=student_headers,
    )
    assert response.status_code == 400


def test_checkin_unenrolled_student_forbidden(
    client: TestClient,
    active_session: SessionResponse,
    unenrolled_student_headers: Headers,
):
    checkin_req = CheckInRequest(lat=21.03824, lng=105.78256)
    response = client.post(
        f"{SESSIONS_URL}/{active_session.id}/check-in",
        json=checkin_req.model_dump(mode="json"),
        headers=unenrolled_student_headers,
    )
    assert response.status_code == 403


def test_checkin_duplicate_conflict(
    client: TestClient,
    active_session: SessionResponse,
    student_headers: Headers,
):
    checkin_req = CheckInRequest(lat=21.03824, lng=105.78256)

    first_res = client.post(
        f"{SESSIONS_URL}/{active_session.id}/check-in",
        json=checkin_req.model_dump(mode="json"),
        headers=student_headers,
    )
    assert first_res.status_code in (200, 201)

    duplicate_res = client.post(
        f"{SESSIONS_URL}/{active_session.id}/check-in",
        json=checkin_req.model_dump(mode="json"),
        headers=student_headers,
    )
    assert duplicate_res.status_code == 409


def test_checkin_within_range_success(
    client: TestClient,
    active_session: SessionResponse,
    student_headers: Headers,
):
    checkin_req = CheckInRequest(lat=21.03824, lng=105.78256)
    response = client.post(
        f"{SESSIONS_URL}/{active_session.id}/check-in",
        json=checkin_req.model_dump(mode="json"),
        headers=student_headers,
    )
    assert response.status_code in (200, 201)

    data = CheckInResponse.model_validate(response.json())
    assert data.status == "PRESENT"
    assert data.distanceMeters <= active_session.radiusMeters


def test_checkin_out_of_range(
    client: TestClient,
    active_session: SessionResponse,
    student_headers: Headers,
):
    checkin_req = CheckInRequest(lat=21.05000, lng=105.85000)
    response = client.post(
        f"{SESSIONS_URL}/{active_session.id}/check-in",
        json=checkin_req.model_dump(mode="json"),
        headers=student_headers,
    )
    assert response.status_code in (200, 201)

    data = CheckInResponse.model_validate(response.json())
    assert data.status == "REJECTED_OUT_OF_RANGE"
    assert data.distanceMeters > active_session.radiusMeters
