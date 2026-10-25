def authenticate_user(login_data: dict):
    # UC1: Authenticate credentials and return a token
    return {
        "accessToken": "eyJhbGciOiJIUzI1Ni...",
        "tokenType": "Bearer",
        "expiresIn": 86400,
        "user": {
            "id": "uuid-user-id",
            "username": "24021625",
            "fullName": "Alex Morgan",
            "email": login_data.get("email"),
            "role": "STUDENT",
        },
    }


def logout_user():
    # UC2: Log out
    return True
