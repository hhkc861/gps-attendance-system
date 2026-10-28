from fastapi import APIRouter, Depends, HTTPException, Path, status
from schemas.reporting_schema import SectionReportResponse, SessionReportResponse
from services.reporting_service import get_section_report, get_session_report
from utils.auth import AuthenticatedUser, get_current_user

router = APIRouter(prefix="/api/reports", tags=["Reporting"])


@router.get(
    "/sessions/{id}",
    response_model=SessionReportResponse,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "description": "Session attendance report retrieved successfully"
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Valid bearer authentication is required"
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Only teachers or administrators can view attendance reports"
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "The attendance session could not be found"
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": "The path parameter is invalid"
        },
    },
    summary="Get attendance report for a session",
    description="Retrieve a detailed attendance report for a specific session.\n\n"
    "Aggregates total sessions held, student attendance breakdown, and overall attendance rates.",
)
def session_report(
    id: int = Path(
        ...,
        title="Session ID",
        description="The unique identifier of the attendance session.",
        examples=[1],
    ),
    user: AuthenticatedUser = Depends(get_current_user),
):
    if user.role not in ("ADMIN", "TEACHER"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only teachers or administrators can view attendance reports",
        )
    try:
        return get_session_report(id)
    except LookupError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )


@router.get(
    "/sections/{id}",
    response_model=SectionReportResponse,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "description": "Section attendance report retrieved successfully"
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Valid bearer authentication is required"
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "The class section could not be found"
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": "The path parameter is invalid"
        },
    },
    summary="Get attendance report for a class section",
    description="Retrieve cumulative attendance statistics for a given class section.\n\n"
    "Aggregates total sessions held, student attendance breakdown, and overall attendance rates.",
    dependencies=[Depends(get_current_user)],
)
def section_report(
    id: int = Path(
        ...,
        title="Class section ID",
        description="The unique identifier of the class section.",
        examples=[1],
    ),
):
    try:
        return get_section_report(id)
    except LookupError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )
