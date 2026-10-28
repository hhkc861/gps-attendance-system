from fastapi.testclient import TestClient
from httpx import Headers

from schemas.reporting_schema import SectionReportResponse, SessionReportResponse
from schemas.section_schema import SectionCreateResponse
from schemas.session_schema import CheckInRequest, SessionResponse

REPORTS_URL = "/api/reports"
SESSIONS_URL = "/api/sessions"


def test_session_report_statistics(
    client: TestClient,
    teacher_headers: Headers,
    student_headers: Headers,
    student2_headers: Headers,
    active_session: SessionResponse,
):
    session_id = active_session.id

    req_1 = CheckInRequest(lat=21.03824, lng=105.78256)
    client.post(
        f"{SESSIONS_URL}/{session_id}/check-in",
        json=req_1.model_dump(mode="json"),
        headers=student_headers,
    )

    req_2 = CheckInRequest(lat=21.05000, lng=105.85000)
    client.post(
        f"{SESSIONS_URL}/{session_id}/check-in",
        json=req_2.model_dump(mode="json"),
        headers=student2_headers,
    )

    response = client.get(
        f"{REPORTS_URL}/sessions/{session_id}",
        headers=teacher_headers,
    )
    assert response.status_code == 200

    report = SessionReportResponse.model_validate(response.json())
    assert report.totalEnrolled == 2
    assert report.presentCount == 1
    assert report.rejectedCount == 1
    assert report.absentCount == 0
    assert report.attendanceRate == 50.0


def test_section_report_cumulative(
    client: TestClient,
    teacher_headers: Headers,
    test_section: SectionCreateResponse,
):
    response = client.get(
        f"{REPORTS_URL}/sections/{test_section.sectionId}",
        headers=teacher_headers,
    )
    assert response.status_code == 200

    report = SectionReportResponse.model_validate(response.json())
    assert report.sectionId == test_section.sectionId
    assert report.totalStudents == 2
    assert isinstance(report.overallAttendanceRate, float)


def test_get_report_not_found(client: TestClient, teacher_headers: Headers):
    fake_id = 999999
    res1 = client.get(f"{REPORTS_URL}/sessions/{fake_id}", headers=teacher_headers)
    assert res1.status_code == 404

    res2 = client.get(f"{REPORTS_URL}/sections/{fake_id}", headers=teacher_headers)
    assert res2.status_code == 404


def test_student_cannot_view_session_report(
    client: TestClient,
    student_headers: Headers,
    active_session: SessionResponse,
):
    res = client.get(
        f"{REPORTS_URL}/sessions/{active_session.id}", headers=student_headers
    )
    assert res.status_code == 403


def test_session_report_with_absent_student(
    client: TestClient,
    teacher_headers: Headers,
    student_headers: Headers,
    active_session: SessionResponse,
):
    session_id = active_session.id
    req_1 = CheckInRequest(lat=21.03824, lng=105.78256)
    client.post(
        f"{SESSIONS_URL}/{session_id}/check-in",
        json=req_1.model_dump(mode="json"),
        headers=student_headers,
    )

    res = client.get(f"{REPORTS_URL}/sessions/{session_id}", headers=teacher_headers)
    assert res.status_code == 200
    report = SessionReportResponse.model_validate(res.json())
    assert report.totalEnrolled == 2
    assert report.presentCount == 1
    assert report.absentCount == 1
