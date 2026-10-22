from fastapi import APIRouter, HTTPException
from services.attendance_service import process_checkin

router = APIRouter(prefix="/api/sessions", tags=["Attendance"])


@router.post("/{id}/checkins", status_code=201)
def checkin(id: str, req: dict):
    try:
        data = process_checkin(id, req.get("lat"), req.get("lng"))
        return {"success": True, "message": "Điểm danh thành công", "data": data}
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "message": "Vị trí nằm ngoài bán kính cho phép",
                "errorCode": "OUT_OF_RANGE",
            },
        )
