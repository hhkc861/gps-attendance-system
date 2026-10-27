from fastapi import APIRouter, Depends, HTTPException, status
from schemas.auth_schema import LoginRequest, LoginResponse, LogoutResponse
from utils.auth import get_current_user
from services.auth_service import InvalidCredentialsError, authenticate_user

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="Log in with username and password",
    description="Log in using a username and password. Returns account information "
    "and a bearer token valid for 30 minutes.",
    responses={
        status.HTTP_200_OK: {
            "description": "Login successful"
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Invalid username or password",
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": "The request body does not match the schema"
        },
    },
)
def login(login_request: LoginRequest) -> LoginResponse:
    try:
        return LoginResponse(data=authenticate_user(login_request))
    except InvalidCredentialsError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        ) from error


@router.post(
    "/logout",
    response_model=LogoutResponse,
    summary="Log out the current session (UC2)",
    description="Clear the token on the client. JWT remains valid until expiration.",
    dependencies=[Depends(get_current_user)],
    responses={401: {"description": "Token is missing, invalid or expired"}},
)
def logout() -> LogoutResponse:
    return LogoutResponse()
