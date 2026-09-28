from flask import Blueprint, request, g
from services.user_service import UserService, UserError
from middleware.auth_middleware import require_auth
from middleware.permission_middleware import require_permission
from utils.response import success, created, error, not_found, server_error

bp = Blueprint("users", __name__)


@bp.get("/")
@require_auth
@require_permission("USER_MANAGEMENT", "view")
def list_users():
    try:
        return success(UserService.list_users(g.user["org_id"]))
    except Exception as e:
        return server_error(str(e))


@bp.get("/<user_id>")
@require_auth
@require_permission("USER_MANAGEMENT", "view")
def get_user(user_id):
    try:
        return success(UserService.get_user(g.user["org_id"], user_id))
    except UserError as e:
        return not_found(str(e))


@bp.post("/")
@require_auth
@require_permission("USER_MANAGEMENT", "create")
def create_user():
    body = request.get_json(silent=True) or {}
    try:
        user = UserService.create_user(
            g.user["org_id"],
            body.get("role_id"),
            body.get("email", ""),
            body.get("password", ""),
            body.get("full_name", ""),
        )
        return created(user)
    except UserError as e:
        return error(str(e))


@bp.put("/<user_id>")
@require_auth
@require_permission("USER_MANAGEMENT", "edit")
def update_user(user_id):
    body = request.get_json(silent=True) or {}
    try:
        user = UserService.update_user(g.user["org_id"], user_id, body)
        return success(user)
    except UserError as e:
        return error(str(e))


@bp.post("/<user_id>/change-password")
@require_auth
def change_password(user_id):
    # Users can change their own password; admins can change anyone's
    body = request.get_json(silent=True) or {}
    org_id = g.user["org_id"]
    requester = g.user["id"]
    if requester != user_id and g.user["role_code"] not in ("super_admin", "hr_manager"):
        from utils.response import forbidden
        return forbidden("You can only change your own password.")
    try:
        UserService.change_password(
            org_id, user_id,
            body.get("current_password", ""),
            body.get("new_password", "")
        )
        return success(None, "Password changed successfully.")
    except UserError as e:
        return error(str(e))


@bp.delete("/<user_id>")
@require_auth
@require_permission("USER_MANAGEMENT", "delete")
def delete_user(user_id):
    try:
        UserService.delete_user(g.user["org_id"], user_id)
        return success(None, "User deleted.")
    except UserError as e:
        return error(str(e))
