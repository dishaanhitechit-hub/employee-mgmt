from extensions import db, to_uuid
from models.department import Department
from models.employee   import Employee


class DepartmentError(Exception):
    pass


class DepartmentService:

    @staticmethod
    def list_departments(org_id: str) -> list[dict]:
        depts = Department.query.filter_by(org_id=to_uuid(org_id)).order_by(Department.name).all()
        return [d.to_dict() for d in depts]

    @staticmethod
    def get_department(org_id: str, dept_id: int) -> dict:
        dept = Department.query.filter_by(id=dept_id, org_id=to_uuid(org_id)).first()
        if not dept:
            raise DepartmentError("Department not found.")
        return dept.to_dict()

    @staticmethod
    def create_department(org_id: str, name: str, description: str = None) -> dict:
        if not name:
            raise DepartmentError("Name is required.")
        if Department.query.filter(
            Department.org_id == to_uuid(org_id),
            Department.name.ilike(name)
        ).first():
            raise DepartmentError(f"Department '{name}' already exists.")
        dept = Department(org_id=to_uuid(org_id), name=name, description=description)
        db.session.add(dept)
        db.session.commit()
        return dept.to_dict()

    @staticmethod
    def update_department(org_id: str, dept_id: int, name: str,
                          description: str = None, head_id: int = None) -> dict:
        dept = Department.query.filter_by(id=dept_id, org_id=to_uuid(org_id)).first()
        if not dept:
            raise DepartmentError("Department not found.")
        conflict = Department.query.filter(
            Department.org_id == to_uuid(org_id),
            Department.name.ilike(name),
            Department.id != dept_id
        ).first()
        if conflict:
            raise DepartmentError(f"Department name '{name}' already taken.")
        if head_id:
            head = Employee.query.filter_by(id=head_id, org_id=to_uuid(org_id)).first()
            if not head:
                raise DepartmentError("Head employee not found.")
        dept.name        = name
        dept.description = description
        dept.head_id     = head_id
        db.session.commit()
        return dept.to_dict()

    @staticmethod
    def delete_department(org_id: str, dept_id: int) -> None:
        dept = Department.query.filter_by(id=dept_id, org_id=to_uuid(org_id)).first()
        if not dept:
            raise DepartmentError("Department not found.")
        active_count = dept.employees.filter_by(employment_status="Active").count()
        if active_count > 0:
            raise DepartmentError("Cannot delete: active employees are assigned to this department.")
        db.session.delete(dept)
        db.session.commit()
