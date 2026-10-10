from utils.haversine import calculate_distance

def open_session_db(class_id: str, request: dict):
    # UC7: Mở phiên điểm danh[cite: 1]
    return {
        "sessionId": "uuid-session-id",
        "classId": class_id,
        "status": "OPEN",
        "startTime": request.get("startTime"),
        "endTime": request.get("endTime")
    }

def close_session_db(session_id: str):
    # UC8: Đóng phiên điểm danh[cite: 1]
    return {"sessionId": session_id, "status": "CLOSED", "closedAt": "2026-09-21T08:10:00Z"}

def process_checkin(session_id: str, lat: float, lng: float):
    # UC9: Xử lý check-in GPS[cite: 1]
    center_lat, center_lng, allowed_radius = 21.038123, 105.782891, 50.0
    distance = calculate_distance(center_lat, center_lng, lat, lng)
    
    if distance > allowed_radius:
        raise ValueError("OUT_OF_RANGE")
        
    return {"recordId": "uuid-record-id", "sessionId": session_id, "distanceMeters": round(distance, 2), "status": "PRESENT"}