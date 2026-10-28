import time
from datetime import datetime, timedelta, timezone
import httpx

BASE_URL = "http://127.0.0.1:8000"


def log_step(msg):
    print(f"\n{'='*20} {msg} {'='*20}")


def run_tests():
    client = httpx.Client(base_url=BASE_URL, timeout=10.0)

    # 1. Đăng nhập Admin
    log_step("1. ĐĂNG NHẬP ADMIN")
    res = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "admin"},
    )
    assert res.status_code == 200, f"Đăng nhập Admin thất bại: {res.text}"
    admin_token = res.json()["data"]["accessToken"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    print("✅ Đăng nhập Admin thành công!")

    # 2. Tạo 1 Giảng viên và 2 Sinh viên
    log_step("2. TẠO TÀI KHOẢN (TEACHER & 2 STUDENTS)")
    ts = int(time.time())
    teacher_uname = f"gv_{ts}"
    sv1_uname = f"sv_trong_lop_{ts}"
    sv2_uname = f"sv_ngoai_lop_{ts}"

    # Tạo Teacher
    res = client.post(
        "/api/users",
        headers=admin_headers,
        json={
            "username": teacher_uname,
            "fullName": "Giang Vien A",
            "password": "Password123!",
            "role": "TEACHER",
        },
    )
    assert res.status_code == 201, f"Tạo Teacher lỗi: {res.text}"

    # Tạo Student 1 (thuộc lớp)
    res = client.post(
        "/api/users",
        headers=admin_headers,
        json={
            "username": sv1_uname,
            "fullName": "Sinh Vien Trong Lop",
            "password": "Password123!",
            "role": "STUDENT",
        },
    )
    assert res.status_code == 201, f"Tạo SV1 lỗi: {res.text}"
    sv1_id = res.json()["id"]

    # Tạo Student 2 (không thuộc lớp)
    res = client.post(
        "/api/users",
        headers=admin_headers,
        json={
            "username": sv2_uname,
            "fullName": "Sinh Vien Ngoai Lop",
            "password": "Password123!",
            "role": "STUDENT",
        },
    )
    assert res.status_code == 201, f"Tạo SV2 lỗi: {res.text}"
    print(f"✅ Đã tạo: {teacher_uname}, {sv1_uname}, {sv2_uname}")

    # 3. Tạo Lớp học phần (Section)
    log_step("3. TẠO SECTION (LỚP HỌC PHẦN)")
    res = client.post(
        "/api/sections",
        headers=admin_headers,
        json={
            "sectionCode": f"SEC_{ts}",
            "teachers": [teacher_uname],
            "students": [sv1_uname],  # Chỉ cho SV1 vào lớp
        },
    )
    assert res.status_code == 201, f"Tạo Section lỗi: {res.text}"
    section_id = res.json()["sectionId"]
    print(f"✅ Tạo Section thành công! Section ID: {section_id}")

    # 4. Teacher đăng nhập và Mở phiên điểm danh (Session)
    log_step("4. TEACHER MỞ PHIÊN ĐIỂM DANH (SESSION)")
    res = client.post(
        "/api/auth/login",
        json={"username": teacher_uname, "password": "Password123!"},
    )
    teacher_token = res.json()["data"]["accessToken"]
    teacher_headers = {"Authorization": f"Bearer {teacher_token}"}

    # Tâm phiên: Nhà E3 - ĐHQGHN (21.03824, 105.78256), Bán kính: 50m
    now = datetime.now(timezone.utc)
    start_time = (now - timedelta(minutes=5)).isoformat()
    end_time = (now + timedelta(minutes=30)).isoformat()

    res = client.post(
        "/api/sessions",
        headers=teacher_headers,
        json={
            "sectionId": section_id,
            "centerLat": 21.03824,
            "centerLng": 105.78256,
            "radiusMeters": 50.0,
            "startTime": start_time,
            "endTime": end_time,
        },
    )
    assert res.status_code == 201, f"Tạo Session lỗi: {res.text}"
    session_id = res.json()["sessionId"]
    print(f"✅ Mở Session thành công! Session ID: {session_id}")

    # 5. SV1 Check-in Trong vùng (PRESENT)
    log_step("5. TEST GPS: SV1 CHECK-IN HỢP LỆ (TRONG VÙNG 50M)")
    res = client.post(
        "/api/auth/login",
        json={"username": sv1_uname, "password": "Password123!"},
    )
    sv1_headers = {"Authorization": f"Bearer {res.json()['data']['accessToken']}"}

    # Tọa độ cách tâm ~8 mét
    res = client.post(
        f"/api/sessions/{session_id}/check-in",
        headers=sv1_headers,
        json={"lat": 21.03829, "lng": 105.78260},
    )
    assert res.status_code == 200, f"Check-in lỗi: {res.text}"
    data = res.json()
    print(
        f"-> Kết quả: status = {data['status']}, khoảng cách = {data['distanceMeters']}m"
    )
    assert data["status"] == "PRESENT", "Lỗi: Đáng lẽ phải là PRESENT"
    assert data["distanceMeters"] <= 50.0, "Lỗi: Khoảng cách phải <= 50m"
    print("✅ TEST 1 ĐẠT: Check-in hợp lệ thành công!")

    # 6. SV1 Check-in Ngoài vùng (REJECTED_OUT_OF_RANGE)
    log_step("6. TEST GPS: SV1 CHECK-IN NGOÀI BÁN KÍNH (HỒ GƯƠM ~7KM)")
    res = client.post(
        f"/api/sessions/{session_id}/check-in",
        headers=sv1_headers,
        json={"lat": 21.0285, "lng": 105.8542},  # Tọa độ Bờ Hồ
    )
    assert res.status_code == 200, f"Check-in lỗi: {res.text}"
    data = res.json()
    print(
        f"-> Kết quả: status = {data['status']}, khoảng cách = {data['distanceMeters']}m"
    )
    assert data["status"] == "REJECTED_OUT_OF_RANGE", "Lỗi: Đáng lẽ phải REJECTED"
    assert data["distanceMeters"] > 5000.0, "Lỗi: Khoảng cách phải > 5km"
    print("✅ TEST 2 ĐẠT: Ngoài vùng bị REJECTED chính xác!")

    # 7. SV2 (không thuộc lớp) cố tình check-in -> Phải bị 403 Forbidden
    log_step("7. TEST BẢO MẬT: SV NGOÀI LỚP CỐ TÌNH CHECK-IN")
    res = client.post(
        "/api/auth/login",
        json={"username": sv2_uname, "password": "Password123!"},
    )
    sv2_headers = {"Authorization": f"Bearer {res.json()['data']['accessToken']}"}

    res = client.post(
        f"/api/sessions/{session_id}/check-in",
        headers=sv2_headers,
        json={"lat": 21.03824, "lng": 105.78256},
    )
    print(f"-> HTTP Status: {res.status_code}, Detail: {res.text}")
    assert res.status_code == 403, "Lỗi: Không thuộc lớp phải trả về 403 Forbidden!"
    print("✅ TEST 3 ĐẠT: Chặn sinh viên ngoài lớp thành công!")

    # 8. Kiểm tra Báo cáo Session (Session Report)
    log_step("8. TEST BÁO CÁO PHIÊN (SESSION REPORT)")
    res = client.get(
        f"/api/reports/sessions/{session_id}",
        headers=teacher_headers,
    )
    assert res.status_code == 200, f"Lấy báo cáo phiên lỗi: {res.text}"
    report = res.json()
    print(f"-> Tổng sinh viên lớp: {report['totalEnrolled']}")
    print(f"-> Số có mặt (Present): {report['presentCount']}")
    print(f"-> Số bị loại (Rejected): {report['rejectedCount']}")
    print(f"-> Tỉ lệ đi học: {report['attendanceRate']}%")
    assert report["totalEnrolled"] == 1
    assert report["rejectedCount"] == 1  # Lần check-in cuối của SV1 là Rejected
    print("✅ TEST 4 ĐẠT: Báo cáo Session thống kê chính xác!")

    # 9. Kiểm tra Báo cáo Section (Section Report)
    log_step("9. TEST BÁO CÁO LỚP HỌC PHẦN (SECTION REPORT)")
    res = client.get(
        f"/api/reports/sections/{section_id}",
        headers=teacher_headers,
    )
    assert res.status_code == 200, f"Lấy báo cáo lớp lỗi: {res.text}"
    sec_report = res.json()
    print(f"-> Tổng số buổi đã mở: {sec_report['totalSessions']}")
    print(f"-> Tỉ lệ tham gia cả lớp: {sec_report['overallAttendanceRate']}%")
    assert sec_report["totalSessions"] == 1
    print("✅ TEST 5 ĐẠT: Báo cáo Section hoạt động chuẩn xác!")

    print("\n🎉 ================================================")
    print("   TẤT CẢ CÁC BÀI TEST ĐÃ VƯỢT QUA XUẤT SẮC!")
    print("================================================\n")


if __name__ == "__main__":
    try:
        run_tests()
    except Exception as e:
        print(f"\n❌ KIỂM TRA THẤT BẠI: {e}")
