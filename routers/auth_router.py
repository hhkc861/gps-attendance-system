from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
import jwt
from schemas.auth_schema import LoginRequest, LoginResponse, LogoutResponse
from utils.auth import bearer_scheme, get_current_user
from services.auth_service import InvalidCredentialsError, authenticate_user, logout_user

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
    description="Revoke the current token. Other login sessions remain active.",
    dependencies=[Depends(get_current_user)],
    responses={status.HTTP_401_UNAUTHORIZED: {"description": "Token is missing, invalid, expired or revoked"}},
)
def logout(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> LogoutResponse:
    try:
        logout_user(credentials.credentials)
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None
    return LogoutResponse()
