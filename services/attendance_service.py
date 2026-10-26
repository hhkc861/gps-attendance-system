from math import radians, sin, cos, sqrt, atan2
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:

    R = 6371000  # Ban kinh Trai Dat (m)
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c

def process_gps_attendance(db: Session, student_id: int, session_id: int, student_lat: float, student_lon: float):

    class_lat = 21.028511
    class_lon = 105.804817
    max_radius = 50.0 #meter

    distance = calculate_distance(student_lat, student_lon, class_lat, class_lon)

    if distance > max_radius:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"You are too far from the classroom ({round(distance, 2)}m). The allowed distance is {max_radius}m."
        )

    return {
        "message": "Attendance marked successfully!",
        "studentId": student_id,
        "sessionId": session_id,
        "distanceMeters": round(distance, 2)
    }
