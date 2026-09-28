from flask import Blueprint, g
from services.permission_service import PermissionService
from middleware.auth_middleware import require_auth
from utils.response import success, server_error

bp = Blueprint("permissions", __name__)


@bp.get("/modules")
@require_auth
def list_modules():

    try:
        return success(PermissionService.list_modules())
    except Exception as e:
        return server_error(str(e))


@bp.get("/my-permissions")
@require_auth
def my_permissions():

    try:
        perms = PermissionService.get_user_permissions(g.user["role_id"])
        return success(perms)
    except Exception as e:
        return server_error(str(e))
