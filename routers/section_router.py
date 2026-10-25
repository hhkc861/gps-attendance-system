from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from schemas.section_schema import SectionCreateRequest, SectionCreateResponse

from services.section_service import create_section as create_section_service
from utils.auth import require_admin

router = APIRouter(prefix="/api/sections", tags=["Sections"])


@router.post(
    "",
    response_model=SectionCreateResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {"description": "Class section created successfully"},
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Valid bearer authentication is required"
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Only administrators can create class sections"
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Invalid data or the class section already exists"
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "One or more accounts could not be found"
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": "The request body does not match the schema"
        },
    },
    summary="Create a class section",
    description="Create a class section using a class code and lists of teacher and student usernames.\n\n"
    "An account cannot be both a teacher and a student in the same section.",
    dependencies=[Depends(require_admin)],
)
def create_section(req: SectionCreateRequest) -> SectionCreateResponse:
    try:
        return create_section_service(req)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )
    except LookupError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )
    except IntegrityError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )
