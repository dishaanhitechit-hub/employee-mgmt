from flask import Blueprint, g
from extensions import db, to_uuid
from models.employee   import Employee
from models.department import Department
from middleware.auth_middleware       import require_auth
from middleware.permission_middleware import require_permission
from utils.response import success, server_error

bp = Blueprint("stats", __name__)


@bp.get("/")
@require_auth
@require_permission("DASHBOARD", "view")
def dashboard_stats():
    try:
        org_id = to_uuid(g.user["org_id"])

        total    = Employee.query.filter_by(org_id=org_id).count()
        active   = Employee.query.filter_by(org_id=org_id, employment_status="Active").count()
        on_leave = Employee.query.filter_by(org_id=org_id, employment_status="On Leave").count()
        inactive = Employee.query.filter_by(org_id=org_id, employment_status="Inactive").count()
        depts    = Department.query.filter_by(org_id=org_id).count()

        # Employment type breakdown
        def count_type(t):
            return Employee.query.filter_by(org_id=org_id, employment_type=t).count()

        emp_types = {
            "full_time": count_type("Full-Time"),
            "part_time": count_type("Part-Time"),
            "contract":  count_type("Contract"),
            "intern":    count_type("Intern"),
        }

        # Per-department headcount
        dept_rows = (
            db.session.query(Department.name, db.func.count(Employee.id))
            .outerjoin(Employee, (Employee.department_id == Department.id) & (Employee.org_id == org_id))
            .filter(Department.org_id == org_id)
            .group_by(Department.name)
            .order_by(db.func.count(Employee.id).desc())
            .all()
        )
        by_dept = [{"department": row[0], "cnt": row[1]} for row in dept_rows]

        return success({
            "headcount":        total,
            "active":           active,
            "on_leave":         on_leave,
            "inactive":         inactive,
            "departments":      depts,
            "employment_types": emp_types,
            "by_department":    by_dept,
        })
    except Exception as exc:
        return server_error(str(exc))
