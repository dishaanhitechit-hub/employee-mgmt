from flask import Blueprint, request, g
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.auth_service import AuthService, AuthError
from middleware.auth_middleware import require_auth
from utils.response import success, error, unauthorized

bp = Blueprint("auth", __name__)


@bp.post("/login")
def login():
    body = request.get_json(silent=True) or {}
    email    = (body.get("email") or "").strip()
    password = body.get("password") or ""
    if not email or not password:
        return error("Email and password are required.", 400)
    try:
        result = AuthService.login(email, password)
        return success(result, "Login successful.")
    except AuthError as e:
        return unauthorized(str(e))


@bp.post("/refresh")
@jwt_required(refresh=True)
def refresh():
    user_id = get_jwt_identity()
    try:
        token = AuthService.refresh_tokens(user_id)
        return success({"access_token": token}, "Token refreshed.")
    except AuthError as e:
        return unauthorized(str(e))


@bp.get("/me")
@require_auth
def me():
    from models.user import User
    from services.permission_service import PermissionService
    user = User.find_by_id(g.user["id"])
    if not user:
        return unauthorized("User not found.")
    perms = PermissionService.get_user_permissions(user["role_id"])
    # strip password_hash before returning
    user.pop("password_hash", None)
    return success({"user": user, "permissions": perms})


@bp.post("/logout")
@require_auth
def logout():
    # JWT is stateless; client discards the token.
    return success(None, "Logged out successfully.")
