from haversine import haversine, Unit


def open_session_db(class_id: str, request: dict):
    # UC7: Open an attendance session
    return {
        "sessionId": "uuid-session-id",
        "classId": class_id,
        "startTime": request.get("startTime"),
        "endTime": request.get("endTime"),
    }


def process_checkin(session_id: str, lat: float, lng: float):
    # UC9: Process GPS check-in
    allowed_radius = 100.0

    center = (21.038123, 105.782891)
    distance = haversine(center, (lat, lng), unit=Unit.METERS)

    if distance > allowed_radius:
        raise ValueError("OUT_OF_RANGE")

    return {
        "recordId": "uuid-record-id",
        "sessionId": session_id,
        "distanceMeters": round(distance, 2),
        "status": "PRESENT",
    }
