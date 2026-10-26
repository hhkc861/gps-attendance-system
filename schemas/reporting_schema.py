from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

AttendanceStatus = Literal["PRESENT", "REJECTED_OUT_OF_RANGE", "ABSENT", "EXCUSED"]


class SessionStudentAttendanceItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    studentId: int = Field(
        title="Student ID",
        description="The unique user ID of the student.",
        examples=[10],
    )
    username: str = Field(
        title="Username",
        description="The student account username / student code.",
        examples=["24021400"],
    )
    fullName: str = Field(
        title="Full name",
        description="The full name of the student.",
        examples=["Nguyen Trong Dai"],
    )
    status: AttendanceStatus = Field(
        title="Attendance status",
        description="The attendance result ('PRESENT', 'REJECTED_OUT_OF_RANGE', 'ABSENT', 'EXCUSED').",
        examples=["PRESENT"],
    )
    lat: Optional[float] = Field(
        default=None,
        title="Latitude",
        description="The device latitude coordinate recorded at check-in.",
        examples=[21.0382],
    )
    lng: Optional[float] = Field(
        default=None,
        title="Longitude",
        description="The device longitude coordinate recorded at check-in.",
        examples=[105.7825],
    )
    distanceMeters: Optional[float] = Field(
        default=None,
        title="Distance in meters",
        description="The computed Haversine distance in meters to the session center.",
        examples=[14.25],
    )
    checkedInAt: Optional[datetime] = Field(
        default=None,
        title="Check-in time",
        description="The timestamp when check-in occurred.",
        examples=["2026-10-26T07:15:30Z"],
    )
    isManuallyOverridden: bool = Field(
        default=False,
        title="Manually overridden flag",
        description="Indicates whether this record was modified manually by a teacher or admin.",
        examples=[False],
    )
    overrideReason: Optional[str] = Field(
        default=None,
        title="Override reason",
        description="The justification or reason provided for manual modification.",
        examples=["Device GPS malfunctioning, confirmed present in classroom"],
    )


class SessionReportResponse(BaseModel):
    sessionId: int = Field(
        title="Session ID",
        description="The unique identifier of the attendance session.",
        examples=[1],
    )
    sectionId: int = Field(
        title="Class section ID",
        description="The ID of the class section.",
        examples=[3],
    )
    sectionCode: str = Field(
        title="Class section code",
        description="The code of the class section.",
        examples=["2627I_INT3105_1"],
    )
    centerLat: float = Field(
        title="Center latitude",
        description="The latitude coordinate for the center of the attendance area.",
        examples=[21.0381],
    )
    centerLng: float = Field(
        title="Center longitude",
        description="The longitude coordinate for the center of the attendance area.",
        examples=[105.7824],
    )
    radiusMeters: float = Field(
        title="Radius in meters",
        description="The allowed geofence radius in meters.",
        examples=[50.0],
    )
    startTime: datetime = Field(
        title="Start time",
        description="The opening time of the attendance session.",
        examples=["2026-10-26T07:00:00Z"],
    )
    endTime: datetime = Field(
        title="End time",
        description="The closing time of the attendance session.",
        examples=["2026-10-26T07:30:00Z"],
    )
    totalEnrolled: int = Field(
        title="Total enrolled students",
        description="Total number of students enrolled in this section.",
        examples=[50],
    )
    presentCount: int = Field(
        title="Present count",
        description="Total students successfully recorded as present.",
        examples=[45],
    )
    rejectedCount: int = Field(
        title="Rejected count",
        description="Total check-ins rejected due to being out of geofence range.",
        examples=[2],
    )
    absentCount: int = Field(
        title="Absent count",
        description="Total students absent from the session.",
        examples=[3],
    )
    excusedCount: int = Field(
        title="Excused count",
        description="Total students with an excused absence.",
        examples=[0],
    )
    attendanceRate: float = Field(
        title="Attendance rate percentage",
        description="The percentage of enrolled students marked as present.",
        examples=[90.0],
    )
    records: list[SessionStudentAttendanceItem] = Field(
        title="Attendance records",
        description="The list of detailed attendance records for all enrolled students.",
    )


class StudentSectionSummaryItem(BaseModel):
    studentId: int = Field(
        title="Student ID",
        description="The unique user ID of the student.",
        examples=[10],
    )
    username: str = Field(
        title="Username",
        description="The student account username / student code.",
        examples=["24021400"],
    )
    fullName: str = Field(
        title="Full name",
        description="The full name of the student.",
        examples=["Nguyen Trong Dai"],
    )
    totalSessions: int = Field(
        title="Total sessions",
        description="Total sessions held for the class section so far.",
        examples=[10],
    )
    presentCount: int = Field(
        title="Present sessions count",
        description="The number of sessions the student attended within range.",
        examples=[9],
    )
    absentCount: int = Field(
        title="Absent sessions count",
        description="The number of sessions the student was marked absent.",
        examples=[1],
    )
    rejectedCount: int = Field(
        title="Rejected check-ins count",
        description="The number of check-in attempts rejected for being out of range.",
        examples=[0],
    )
    excusedCount: int = Field(
        title="Excused sessions count",
        description="The number of sessions excused for the student.",
        examples=[0],
    )
    attendanceRate: float = Field(
        title="Attendance rate percentage",
        description="The attendance percentage of the student for this section.",
        examples=[90.0],
    )


class SectionReportResponse(BaseModel):
    sectionId: int = Field(
        title="Class section ID",
        description="The unique ID of the class section.",
        examples=[1],
    )
    sectionCode: str = Field(
        title="Class section code",
        description="The code of the class section.",
        examples=["2627I_INT3105_1"],
    )
    totalSessions: int = Field(
        title="Total sessions",
        description="Total attendance sessions opened for this section.",
        examples=[15],
    )
    totalStudents: int = Field(
        title="Total enrolled students",
        description="Total number of students enrolled in this section.",
        examples=[60],
    )
    overallAttendanceRate: float = Field(
        title="Overall attendance rate percentage",
        description="Average attendance percentage across all enrolled students and sessions.",
        examples=[92.5],
    )
    students: list[StudentSectionSummaryItem] = Field(
        title="Students summary",
        description="The list of aggregated attendance metrics for each enrolled student.",
    )


class StudentHistoryItem(BaseModel):
    sessionId: int = Field(
        title="Session ID",
        description="The unique identifier of the attendance session.",
        examples=[5],
    )
    sectionCode: str = Field(
        title="Class section code",
        description="The code of the class section.",
        examples=["2627I_INT3105_1"],
    )
    sessionTime: datetime = Field(
        title="Session time",
        description="The start time of the session.",
        examples=["2026-10-26T07:00:00Z"],
    )
    status: AttendanceStatus = Field(
        title="Attendance status",
        description="The final recorded attendance status.",
        examples=["PRESENT"],
    )
    distanceMeters: Optional[float] = Field(
        default=None,
        title="Distance in meters",
        description="The computed GPS distance in meters to the session center.",
        examples=[12.5],
    )
    checkedInAt: Optional[datetime] = Field(
        default=None,
        title="Check-in time",
        description="The timestamp when check-in occurred.",
        examples=["2026-10-26T07:05:00Z"],
    )
    isManuallyOverridden: bool = Field(
        default=False,
        title="Manually overridden flag",
        description="True if the status was adjusted manually.",
        examples=[False],
    )


class StudentReportResponse(BaseModel):
    studentId: int = Field(
        title="Student ID",
        description="The unique user ID of the student.",
        examples=[10],
    )
    username: str = Field(
        title="Username",
        description="The student account username / student code.",
        examples=["24021400"],
    )
    fullName: str = Field(
        title="Full name",
        description="The full name of the student.",
        examples=["Nguyen Trong Dai"],
    )
    totalSessions: int = Field(
        title="Total sessions",
        description="The total number of sessions eligible for attendance.",
        examples=[20],
    )
    attendedSessions: int = Field(
        title="Attended sessions",
        description="The number of sessions successfully attended (status PRESENT).",
        examples=[18],
    )
    attendanceRate: float = Field(
        title="Attendance rate percentage",
        description="The cumulative attendance percentage for the student.",
        examples=[90.0],
    )
    history: list[StudentHistoryItem] = Field(
        title="Attendance history",
        description="Chronological log of individual session attendance results.",
    )
