# Hệ thống Điểm danh qua GPS

> [!NOTE]
> WORKING IN PROGRESS
>

Kho lưu trữ (repository) này cung cấp phần backend xây dựng bằng FastAPI cho hệ thống điểm danh lớp học dựa trên định vị GPS. Giáo viên có thể mở các phiên điểm danh cho một lớp học, sinh viên có thể thực hiện điểm danh từ một vùng địa lý (geofence) đã được thiết lập, và hệ thống sẽ xuất báo cáo điểm danh theo từng phiên hoặc theo từng lớp học phần.

## Các tính năng của API

- Xác thực người dùng bằng JWT bearer token
- Phân quyền theo vai trò: ADMIN, TEACHER, STUDENT
- Tạo và liệt kê tài khoản; chỉ admin mới có quyền tạo/xóa tài khoản
- Tạo lớp học phần (section), chỉ định giáo viên phụ trách và thêm sinh viên vào lớp
- Tạo phiên điểm danh bằng cách thiết lập tâm GPS + bán kính + khung thời gian
- Xác thực điểm danh của sinh viên bằng công thức tính khoảng cách Haversine
- Xuất báo cáo điểm danh theo từng phiên và theo từng lớp học phần
- Hỗ trợ thu hồi token (token revocation) khi đăng xuất

## Tech stack (Công nghệ sử dụng)

- Python 3
- FastAPI
- SQLAlchemy + PostgreSQL
- Pydantic validation
- JWT authentication
- Docker Compose for PostgreSQL

## Quick start (Bắt đầu chạy)

1. Cài đặt Docker Desktop và đảm bảo ứng dụng đang chạy.
2. Sao chép và đổi tên tệp `.env.example` thành  `.env`
3. Khởi chạy PostgreSQL:

```bash
docker compose up -d --wait postgres
```

4. Cài đặt các thư viện phụ thuộc của Python:

```bash
python -m pip install -r requirements.txt
```

5. Khởi chạy API:

```bash
uvicorn main:app --reload
```

Ứng dụng có thể truy cập tại:

- OpenAPI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc
- Health root: http://127.0.0.1:8000/

## Biến môi trường

Dự án đọc các thiết lập cấu hình từ tệp `.env`:

```env
DATABASE_URL=postgresql+psycopg://attendance:attendance@localhost:5432/gps_attendance
JWT_SECRET=replace-with-a-long-random-secret
BOOTSTRAP_ADMIN_PASSWORD=replace-with-a-strong-password
```

Nếu `BOOTSTRAP_ADMIN_PASSWORD` được thiết lập, API sẽ tự động tạo một tài khoản quản trị viên ban đầu với tên đăng nhập là `admin` khi hệ thống khởi động.

## Xác thực

Sử dụng JWT bearer token được trả về từ endpoint `/api/auth/login`.

```http
Authorization: Bearer <access_token>
```

Token sẽ hết hạn sau 30 phút hoặc khi người dùng thực hiện thao tác đăng xuất thủ công.

## Các endpoint chính

| Phân loại | Endpoint | Mục đích |
|---|---|---|
| Auth | `POST /api/auth/login` | Đăng nhập và nhận JWT token |
| Auth | `POST /api/auth/logout` | Đăng xuất token hiện tại |
| Users | `POST /api/users` | Tạo tài khoản (chỉ dành cho admin) |
| Users | `GET /api/users` | Lấy danh sách người dùng kèm bộ lọc vai trò/tìm kiếm và phân trang |
| Users | `DELETE /api/users/{id}` | Xóa tài khoản (chỉ dành cho admin) |
| Sections | `POST /api/sections` | Tạo lớp học phần kèm danh sách giáo viên và sinh viên |
| Sessions | `POST /api/sessions` | Mở một phiên điểm danh |
| Sessions | `POST /api/sessions/{id}/check-in` | Xác thực điểm danh bằng GPS của sinh viên |
| Reports | `GET /api/reports/sessions/{id}` | Lấy báo cáo cho một phiên điểm danh |
| Reports | `GET /api/reports/sections/{id}` | Lấy báo cáo tổng hợp cho một lớp học phần |

## Quy tắc điểm danh

- Một phiên điểm danh sẽ xác định một vùng địa lý (geofence) thông qua tọa độ tâm, bán kính tính theo mét và một khung thời gian cho phép.
- Tọa độ điểm danh của sinh viên được đánh giá và tính toán bằng công thức Haversine.
- Các trạng thái điểm danh:
  - `PRESENT` khi thiết bị nằm trong bán kính hợp lệ
  - `REJECTED_OUT_OF_RANGE` khi thiết bị nằm ngoài bán kính hợp lệ
  - `ABSENT` / `EXCUSED` được sử dụng trong logic tổng hợp báo cáo
- Chỉ những người dùng đã được thêm vào lớp học phần mới có thể điểm danh cho phiên điểm danh của lớp đó.
- Chỉ người dùng có vai trò TEACHER và ADMIN mới có quyền mở phiên điểm danh hoặc xem báo cáo điểm danh.

## Quy trình hoạt động thông thường

1. Admin tạo tài khoản cho cán bộ giảng viên và sinh viên.
2. Admin tạo lớp học phần và gán giáo viên/sinh viên vào lớp.
3. Giáo viên đăng nhập và mở một phiên điểm danh kèm thiết lập vùng geofence của lớp.
4. Sinh viên đăng nhập và gửi tọa độ GPS lên endpoint `/api/sessions/{id}/check-in`.
5. Giáo viên lấy dữ liệu báo cáo từ `/api/reports/sessions/{id}` hoặc `/api/reports/sections/{id}`.

## Đề xuất cải thiện cho Phase 2 (Roadmap)

| Phân loại | Tính năng đề xuất | Mục đích & Giải pháp kỹ thuật |
|---|---|---|
| Chống gian lận | Khóa thiết bị (Device Binding) | Ràng buộc 1 tài khoản chỉ được điểm danh trên 1 thiết bị (Device UUID) nhằm chống đăng nhập hộ. |
| Chống gian lận | Phát hiện Mock Location / Fake GPS | Chặn các ứng dụng giả lập tọa độ GPS trên thiết bị di động của sinh viên. |
| Chống gian lận | Xác thực phụ trợ (Wi-Fi BSSID / Dynamic QR) | Khắc phục sai số GPS trong phòng học kín bằng cách kiểm tra Wi-Fi trường hoặc quét thêm mã QR động trên màn chiếu. |
| Nghiệp vụ | Thêm trạng thái Đi trễ (`LATE`) | Bổ sung mốc thời gian phụ: sinh viên check-in sau giờ quy định sẽ tính là đi trễ thay vì vắng mặt. |
| Nghiệp vụ | Đơn xin phép vắng (`EXCUSED`) | Cung cấp API cho sinh viên nộp đơn xin nghỉ phép kèm minh chứng, giáo viên duyệt để cập nhật trạng thái. |
| Nghiệp vụ | Điểm danh thủ công (Manual Override) | Cho phép giáo viên can thiệp sửa trạng thái điểm danh cho sinh viên gặp sự cố hỏng máy, hết pin. |
| Báo cáo & Dữ liệu | Import/Export Excel & CSV | Hỗ trợ admin nhập hàng loạt sinh viên vào lớp và cho phép giáo viên xuất báo cáo điểm danh ra file `.xlsx` / `.pdf`. |
| Báo cáo & Dữ liệu | Cảnh báo học vụ tự động | Tự động tính tỷ lệ chuyên cần và gắn cờ cảnh báo các sinh viên nghỉ quá 20% số buổi (nguy cơ cấm thi). |
| Hệ thống | Bổ sung Refresh Token | Duy trì phiên đăng nhập cho người dùng mượt mà hơn thay vì bị ngắt kết nối sau mỗi 30 phút. |
| Hệ thống | Tích hợp Redis | Lưu trữ danh sách token đã thu hồi (blacklist), cache cấu hình session đang mở và hỗ trợ Rate Limiting chống spam API. |
| Hệ thống | Cập nhật thời gian thực (WebSocket / SSE) | Hiển thị danh sách sinh viên vừa điểm danh thành công lên màn hình giáo viên theo thời gian thực. |
| Hệ thống | Tác vụ chạy nền (Background Tasks) | Tự động quét và chốt trạng thái `ABSENT` cho các sinh viên không điểm danh ngay khi hết khung giờ session. |
| Hạ tầng | Database Migration (Alembic) | Quản lý lịch sử và cập nhật schema cơ sở dữ liệu PostgreSQL một cách có hệ thống. |
| Hạ tầng | Full Dockerization | Đưa toàn bộ mã nguồn FastAPI vào file `docker-compose.yml` để dễ dàng đóng gói và triển khai CI/CD. |
