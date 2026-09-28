from flask import Blueprint, request, g
from services.organization_service import OrganizationService, OrgError
from middleware.auth_middleware import require_auth
from utils.response import success, created, error, not_found, server_error

bp = Blueprint("organizations", __name__)


@bp.get("/")
@require_auth
def list_orgs():
    # Only super-admins would call this; route is here for completeness
    try:
        return success(OrganizationService.list_all())
    except Exception as e:
        return server_error(str(e))


@bp.get("/me")
@require_auth
def my_org():
    try:
        org = OrganizationService.get(g.user["org_id"])
        return success(org)
    except OrgError as e:
        return not_found(str(e))


@bp.post("/")
@require_auth
def create_org():
    body = request.get_json(silent=True) or {}
    try:
        org = OrganizationService.create(
            body.get("name", ""), body.get("domain", ""), body.get("plan", "starter")
        )
        return created(org)
    except OrgError as e:
        return error(str(e))


@bp.put("/<org_id>")
@require_auth
def update_org(org_id):
    body = request.get_json(silent=True) or {}
    try:
        org = OrganizationService.update(
            org_id,
            body.get("name", ""),
            body.get("domain", ""),
            body.get("plan", "starter"),
            body.get("is_active", True),
        )
        return success(org)
    except OrgError as e:
        return error(str(e))
