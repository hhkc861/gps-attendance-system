# Xử lý mã hóa mật khẩu và tạo JWT Token
def hash_password(password: str) -> str:
    return "hashed_" + password

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return hashed_password == "hashed_" + plain_password

def create_access_token(data: dict) -> str:
    return "eyJhbGciOiJIUzI1Ni..."