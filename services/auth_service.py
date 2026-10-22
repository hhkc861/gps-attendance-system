def authenticate_user(login_data: dict):
    # UC1: Xác thực thông tin và trả về token
    return {
        "accessToken": "eyJhbGciOiJIUzI1Ni...",
        "tokenType": "Bearer",
        "expiresIn": 86400,
        "user": {
            "id": "uuid-user-id",
            "code": "24021625",
            "fullName": "Nguyễn Văn A",
            "email": login_data.get("email"),
            "role": "STUDENT",
        },
    }


def logout_user():
    # UC2: Đăng xuất
    return True
