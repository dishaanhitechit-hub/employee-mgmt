from flask import Blueprint, request, g
from middleware.auth_middleware       import require_auth
from middleware.permission_middleware import require_permission
from services.attendance_service      import AttendanceService, AttendanceError
from utils.response import success, created, error, not_found, server_error

bp = Blueprint("attendance", __name__)


@bp.get("/")
@require_auth
@require_permission("ATTENDANCE", "view")
def list_attendance():
    try:
        records = AttendanceService.list_attendance(g.user["org_id"], dict(request.args))
        return success(records, meta={"count": len(records)})
    except Exception as e:
        return server_error(str(e))


@bp.get("/summary")
@require_auth
@require_permission("ATTENDANCE", "view")
def attendance_summary():
    try:
        return success(AttendanceService.summary(g.user["org_id"], dict(request.args)))
    except Exception as e:
        return server_error(str(e))


@bp.get("/<int:attendance_id>")
@require_auth
@require_permission("ATTENDANCE", "view")
def get_attendance(attendance_id):
    try:
        return success(AttendanceService.get_attendance(g.user["org_id"], attendance_id))
    except AttendanceError as e:
        return not_found(str(e))
    except Exception as e:
        return server_error(str(e))


@bp.post("/")
@require_auth
@require_permission("ATTENDANCE", "create")
def mark_attendance():
    data = request.get_json(silent=True) or {}
    try:
        record = AttendanceService.mark_attendance(g.user["org_id"], data, g.user["id"])
        return created(record)
    except AttendanceError as e:
        return error(str(e))
    except Exception as e:
        return server_error(str(e))


@bp.post("/bulk")
@require_auth
@require_permission("ATTENDANCE", "create")
def bulk_mark():
    data = request.get_json(silent=True) or {}
    date_str = data.get("date")
    records  = data.get("records", [])
    if not date_str:
        return error("'date' is required.")
    if not isinstance(records, list) or not records:
        return error("'records' must be a non-empty list.")
    try:
        result = AttendanceService.bulk_mark(g.user["org_id"], date_str, records, g.user["id"])
        return success(result, meta={"count": len(result)})
    except AttendanceError as e:
        return error(str(e))
    except Exception as e:
        return server_error(str(e))


@bp.put("/<int:attendance_id>")
@require_auth
@require_permission("ATTENDANCE", "edit")
def update_attendance(attendance_id):
    data = request.get_json(silent=True) or {}
    try:
        record = AttendanceService.update_attendance(g.user["org_id"], attendance_id, data, g.user["id"])
        return success(record)
    except AttendanceError as e:
        return error(str(e))
    except Exception as e:
        return server_error(str(e))


@bp.delete("/<int:attendance_id>")
@require_auth
@require_permission("ATTENDANCE", "delete")
def delete_attendance(attendance_id):
    try:
        AttendanceService.delete_attendance(g.user["org_id"], attendance_id)
        return success(None, "Attendance record deleted.")
    except AttendanceError as e:
        return error(str(e))
    except Exception as e:
        return server_error(str(e))
