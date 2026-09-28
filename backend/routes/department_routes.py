from flask import Blueprint, request, g
from services.department_service import DepartmentService, DepartmentError
from middleware.auth_middleware import require_auth
from middleware.permission_middleware import require_permission
from utils.response import success, created, error, not_found, server_error

bp = Blueprint("departments", __name__)


@bp.get("/")
@require_auth
@require_permission("DEPARTMENTS", "view")
def list_departments():
    try:
        return success(DepartmentService.list_departments(g.user["org_id"]))
    except Exception as e:
        return server_error(str(e))


@bp.get("/<int:dept_id>")
@require_auth
@require_permission("DEPARTMENTS", "view")
def get_department(dept_id):
    try:
        return success(DepartmentService.get_department(g.user["org_id"], dept_id))
    except DepartmentError as e:
        return not_found(str(e))


@bp.post("/")
@require_auth
@require_permission("DEPARTMENTS", "create")
def create_department():
    body = request.get_json(silent=True) or {}
    try:
        dept = DepartmentService.create_department(
            g.user["org_id"],
            body.get("name", ""),
            body.get("description"),
        )
        return created(dept)
    except DepartmentError as e:
        return error(str(e))


@bp.put("/<int:dept_id>")
@require_auth
@require_permission("DEPARTMENTS", "edit")
def update_department(dept_id):
    body = request.get_json(silent=True) or {}
    try:
        dept = DepartmentService.update_department(
            g.user["org_id"], dept_id,
            body.get("name", ""),
            body.get("description"),
            body.get("head_id"),
        )
        return success(dept)
    except DepartmentError as e:
        return error(str(e))


@bp.delete("/<int:dept_id>")
@require_auth
@require_permission("DEPARTMENTS", "delete")
def delete_department(dept_id):
    try:
        DepartmentService.delete_department(g.user["org_id"], dept_id)
        return success(None, "Department deleted.")
    except DepartmentError as e:
        return error(str(e))
