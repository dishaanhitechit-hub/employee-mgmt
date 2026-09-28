from flask import Blueprint, request, g
from services.role_service import RoleService, RoleError
from middleware.auth_middleware import require_auth
from middleware.permission_middleware import require_permission
from utils.response import success, created, error, not_found, server_error

bp = Blueprint("roles", __name__)


@bp.get("/")
@require_auth
@require_permission("ROLE_MANAGEMENT", "view")
def list_roles():
    try:
        return success(RoleService.list_roles(g.user["org_id"]))
    except Exception as e:
        return server_error(str(e))


@bp.get("/<int:role_id>")
@require_auth
@require_permission("ROLE_MANAGEMENT", "view")
def get_role(role_id):
    try:
        return success(RoleService.get_role(g.user["org_id"], role_id))
    except RoleError as e:
        return not_found(str(e))


@bp.post("/")
@require_auth
@require_permission("ROLE_MANAGEMENT", "create")
def create_role():
    body = request.get_json(silent=True) or {}
    try:
        role = RoleService.create_role(
            g.user["org_id"],
            body.get("name", ""),
            body.get("code", ""),
            body.get("description"),
        )
        return created(role)
    except RoleError as e:
        return error(str(e))


@bp.put("/<int:role_id>")
@require_auth
@require_permission("ROLE_MANAGEMENT", "edit")
def update_role(role_id):
    body = request.get_json(silent=True) or {}
    try:
        role = RoleService.update_role(
            g.user["org_id"], role_id,
            body.get("name", ""), body.get("description")
        )
        return success(role)
    except RoleError as e:
        return error(str(e))


@bp.put("/<int:role_id>/permissions")
@require_auth
@require_permission("ROLE_MANAGEMENT", "edit")
def set_permissions(role_id):

    body = request.get_json(silent=True) or {}
    permissions = body.get("permissions", [])
    try:
        role = RoleService.set_permissions(g.user["org_id"], role_id, permissions)
        return success(role)
    except RoleError as e:
        return error(str(e))


@bp.delete("/<int:role_id>")
@require_auth
@require_permission("ROLE_MANAGEMENT", "delete")
def delete_role(role_id):
    try:
        RoleService.delete_role(g.user["org_id"], role_id)
        return success(None, "Role deleted.")
    except RoleError as e:
        return error(str(e))
