from functools import wraps
from flask import g
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
from utils.response import unauthorized


def require_auth(f):
    @wraps(f)
    def _wrapped(*args, **kwargs):
        try:
            verify_jwt_in_request()
            claims = get_jwt()
            g.user = {
                "id":            get_jwt_identity(),
                "org_id":        claims.get("org_id"),
                "role_id":       claims.get("role_id"),
                "role_code":     claims.get("role_code"),
                "email":         claims.get("email"),
                "full_name":     claims.get("full_name"),
                "employee_id":   claims.get("employee_id"),
                "department_id": claims.get("department_id"),
            }
        except Exception as exc:
            return unauthorized(str(exc))
        return f(*args, **kwargs)
    return _wrapped
