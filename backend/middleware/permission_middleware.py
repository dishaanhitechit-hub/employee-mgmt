from functools import wraps
from flask import g
from models.permission            import RolePermission
from models.employee_permission   import EmployeePermission
from models.department_permission import DepartmentPermission
from models.module                import Module
from utils.response               import forbidden

_ACTION_COL = {
    "view":   "can_view",
    "create": "can_create",
    "edit":   "can_edit",
    "delete": "can_delete",
}


def _resolve_permission(module_code: str):
    """
    Returns the effective permission row for the current user on a module.
    Priority (highest → lowest):
      1. Department permission  — overrides everything if set
      2. Employee permission    — individual override
      3. Role permission        — default baseline
    Returns None if no permission is found at any level.
    """
    role_id    = g.user.get("role_id")
    emp_id     = g.user.get("employee_id")   # may be None (non-employee user)
    dept_id    = g.user.get("department_id") # may be None

    module = Module.query.filter_by(code=module_code).first()
    if not module:
        return None

    # 1. Department permission (highest priority)
    if dept_id:
        perm = DepartmentPermission.query.filter_by(
            department_id=dept_id, module_id=module.id
        ).first()
        if perm:
            return perm

    # 2. Employee permission
    if emp_id:
        perm = EmployeePermission.query.filter_by(
            employee_id=emp_id, module_id=module.id
        ).first()
        if perm:
            return perm

    # 3. Role permission (baseline)
    return RolePermission.query.filter_by(
        role_id=role_id, module_id=module.id
    ).first()


def require_permission(module_code: str, action: str = "view"):
    def decorator(f):
        @wraps(f)
        def _wrapped(*args, **kwargs):
            perm = _resolve_permission(module_code)
            if not perm:
                return forbidden(f"No access to module '{module_code}'.")
            col = _ACTION_COL.get(action, "can_view")
            if not getattr(perm, col, False):
                return forbidden(f"No '{action}' permission on module '{module_code}'.")
            return f(*args, **kwargs)
        return _wrapped
    return decorator
