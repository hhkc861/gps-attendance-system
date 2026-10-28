from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.exc import IntegrityError
from schemas.session_schema import CheckInRequest, CheckInResponse, SessionCreateRequest
from services.session_service import open_session, process_checkin
from utils.auth import AuthenticatedUser, get_current_user

router = APIRouter(prefix="/api/sessions", tags=["Sessions"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {
            "description": "Attendance session opened successfully"
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Invalid time window or invalid coordinates"
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Valid bearer authentication is required"
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Only teachers or administrators can open an attendance session"
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "The class section could not be found"
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": "The request body does not match the schema"
        },
    },
    summary="Open an attendance session",
    description="Open a new attendance session for a class section using GPS coordinates, radius, and time window.\n\n"
    "Only teachers or administrators are permitted to create sessions.",
)
def create_session(
    req: SessionCreateRequest,
    user: AuthenticatedUser = Depends(get_current_user),
):
    if user.role not in ("ADMIN", "TEACHER"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only teachers or administrators can open an attendance session",
        )
    try:
        session = open_session(
            section_id=req.sectionId,
            center_lat=req.centerLat,
            center_lng=req.centerLng,
            radius=req.radiusMeters,
            start_time=req.startTime,
            end_time=req.endTime,
        )
        return {"success": True, "sessionId": session.id}
    except LookupError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )


@router.post(
    "/{id}/check-in",
    response_model=CheckInResponse,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "description": "Check-in processed successfully",
            "model": CheckInResponse,
        },
        status.HTTP_400_BAD_REQUEST: {"description": "Session is not currently active"},
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Valid bearer authentication is required"
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "The student is not enrolled in this class section"
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "The attendance session could not be found"
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": "The request body does not match the schema"
        },
    },
    summary="Process GPS check-in for a session",
    description="Process student GPS check-in against the session geofence.\n\n"
    "Calculates distance using the Haversine formula. If distance <= radius, status is PRESENT; "
    "otherwise status is REJECTED_OUT_OF_RANGE.",
)
def check_in(
    req: CheckInRequest,
    id: int = Path(
        ...,
        title="Session ID",
        description="The ID of the session to check in to.",
        examples=[1],
    ),
    user: AuthenticatedUser = Depends(get_current_user),
) -> CheckInResponse:
    try:
        return process_checkin(
            session_id=id,
            student_id=user.id,
            lat=req.lat,
            lng=req.lng,
        )
    except LookupError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )
    except PermissionError as error:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(error),
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )
