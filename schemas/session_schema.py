from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

AttendanceStatus = Literal["PRESENT", "REJECTED_OUT_OF_RANGE", "ABSENT", "EXCUSED"]


class SessionCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sectionId: int = Field(
        title="Class section ID",
        description="The unique identifier of the class section.",
        examples=[1],
    )
    centerLat: float = Field(
        ge=-90.0,
        le=90.0,
        title="Center latitude",
        description="The latitude coordinate for the center of the attendance area.",
        examples=[21.03824],
    )
    centerLng: float = Field(
        ge=-180.0,
        le=180.0,
        title="Center longitude",
        description="The longitude coordinate for the center of the attendance area.",
        examples=[105.78256],
    )
    radiusMeters: float = Field(
        gt=0.0,
        le=5000.0,
        title="Radius in meters",
        description="The maximum allowed distance from center in meters for valid check-in.",
        examples=[50.0],
    )
    startTime: datetime = Field(
        title="Start time",
        description="The opening timestamp of the attendance window.",
        examples=["2026-10-26T07:00:00Z"],
    )
    endTime: datetime = Field(
        title="End time",
        description="The closing timestamp of the attendance window.",
        examples=["2026-10-26T07:30:00Z"],
    )

    @model_validator(mode="after")
    def validate_time_window(self):
        if self.endTime <= self.startTime:
            raise ValueError("End time must be after start time")
        return self


class SessionResponse(BaseModel):
    id: int = Field(
        title="Session ID",
        description="The unique identifier of the attendance session.",
        examples=[1],
    )
    sectionId: int = Field(
        title="Class section ID",
        description="The ID of the associated class section.",
        examples=[1],
    )
    centerLat: float = Field(
        title="Center latitude",
        description="The latitude coordinate for the center of the attendance area.",
        examples=[21.03824],
    )
    centerLng: float = Field(
        title="Center longitude",
        description="The longitude coordinate for the center of the attendance area.",
        examples=[105.78256],
    )
    radiusMeters: float = Field(
        title="Radius in meters",
        description="The maximum allowed check-in radius in meters.",
        examples=[50.0],
    )
    startTime: datetime = Field(
        title="Start time",
        description="The opening timestamp of the attendance session.",
        examples=["2026-10-26T07:00:00Z"],
    )
    endTime: datetime = Field(
        title="End time",
        description="The closing timestamp of the attendance session.",
        examples=["2026-10-26T07:30:00Z"],
    )
    createdAt: datetime = Field(
        title="Creation time",
        description="The timestamp when the session was created.",
        examples=["2026-10-26T06:55:00Z"],
    )


class CheckInRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    lat: float = Field(
        ge=-90.0,
        le=90.0,
        title="Latitude",
        description="The latitude coordinate reported by the student device.",
        examples=[21.03831],
    )
    lng: float = Field(
        ge=-180.0,
        le=180.0,
        title="Longitude",
        description="The longitude coordinate reported by the student device.",
        examples=[105.78261],
    )


class CheckInResponse(BaseModel):
    recordId: int = Field(
        title="Record ID",
        description="The unique identifier of the created attendance record.",
        examples=[100],
    )
    sessionId: int = Field(
        title="Session ID",
        description="The ID of the session checked in to.",
        examples=[1],
    )
    studentId: int = Field(
        title="Student ID",
        description="The unique user ID of the student.",
        examples=[12],
    )
    distanceMeters: float = Field(
        title="Distance in meters",
        description="The calculated distance in meters from student position to session center.",
        examples=[9.35],
    )
    status: AttendanceStatus = Field(
        title="Attendance status",
        description="The attendance outcome: 'PRESENT' or 'REJECTED_OUT_OF_RANGE'.",
        examples=["PRESENT"],
    )
    checkedInAt: datetime = Field(
        title="Check-in time",
        description="The exact timestamp when the check-in was processed.",
        examples=["2026-10-26T07:05:12Z"],
    )
    message: str = Field(
        title="Result message",
        description="A human-readable status message regarding the check-in attempt.",
        examples=["Check-in successful (within range)"],
    )
