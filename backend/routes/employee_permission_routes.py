from flask import Blueprint, g, request
from middleware.auth_middleware       import require_auth
from middleware.permission_middleware import require_permission
from services.employee_permission_service import EmployeePermissionService
from utils.response import success, error, server_error

bp = Blueprint("employee_permissions", __name__)


@bp.get("/<int:employee_id>")
@require_auth
@require_permission("ROLE_MANAGEMENT", "view")
def get_employee_permissions(employee_id):
    try:
        return success(EmployeePermissionService.get_employee_permissions(employee_id))
    except ValueError as e:
        return error(str(e), 404)
    except Exception as e:
        return server_error(str(e))


@bp.put("/<int:employee_id>")
@require_auth
@require_permission("ROLE_MANAGEMENT", "edit")
def save_employee_permissions(employee_id):
    data = request.get_json() or {}
    permissions = data.get("permissions", [])
    if not isinstance(permissions, list):
        return error("'permissions' must be a list.", 400)
    try:
        return success(EmployeePermissionService.save_employee_permissions(employee_id, permissions))
    except ValueError as e:
        return error(str(e), 404)
    except Exception as e:
        return server_error(str(e))


@bp.delete("/<int:employee_id>")
@require_auth
@require_permission("ROLE_MANAGEMENT", "edit")
def clear_employee_permissions(employee_id):
    try:
        EmployeePermissionService.clear_employee_permissions(employee_id)
        return success({"message": "All individual overrides cleared."})
    except Exception as e:
        return server_error(str(e))
