from flask import Blueprint, request, g
from services.employee_service import EmployeeService, EmployeeError
from middleware.auth_middleware import require_auth
from middleware.permission_middleware import require_permission
from utils.response import success, created, error, not_found, server_error

bp = Blueprint("employees", __name__)


@bp.get("/")
@require_auth
@require_permission("EMPLOYEES", "view")
def list_employees():
    try:
        employees = EmployeeService.list_employees(g.user["org_id"], dict(request.args))
        return success(employees, meta={"count": len(employees)})
    except Exception as e:
        return server_error(str(e))


@bp.get("/<employee_id>")
@require_auth
@require_permission("EMPLOYEES", "view")
def get_employee(employee_id):
    try:
        emp = EmployeeService.get_employee(g.user["org_id"], employee_id)
        return success(emp)
    except EmployeeError as e:
        return not_found(str(e))


@bp.post("/")
@require_auth
@require_permission("EMPLOYEES", "create")
def create_employee():
    data = request.get_json(silent=True) or {}
    try:
        emp = EmployeeService.create_employee(g.user["org_id"], data)
        return created(emp)
    except EmployeeError as e:
        return error(str(e))


@bp.put("/<employee_id>")
@require_auth
@require_permission("EMPLOYEES", "edit")
def update_employee(employee_id):
    data = request.get_json(silent=True) or {}
    try:
        emp = EmployeeService.update_employee(g.user["org_id"], employee_id, data)
        return success(emp)
    except EmployeeError as e:
        return error(str(e))


@bp.delete("/<employee_id>")
@require_auth
@require_permission("EMPLOYEES", "delete")
def delete_employee(employee_id):
    try:
        EmployeeService.delete_employee(g.user["org_id"], employee_id)
        return success(None, f"Employee {employee_id} deleted.")
    except EmployeeError as e:
        return error(str(e))
