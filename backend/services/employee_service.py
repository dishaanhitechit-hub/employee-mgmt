from extensions import db, to_uuid
from models.employee   import Employee
from models.department import Department
from models.skill      import Skill, employee_skills
from utils.validators  import validate_email, validate_phone


class EmployeeError(Exception):
    pass


class EmployeeService:

    @staticmethod
    def _next_employee_id(org_id) -> str:
        last = (
            Employee.query
            .filter_by(org_id=org_id)
            .order_by(Employee.id.desc())
            .first()
        )
        if not last:
            return "EMP001"
        num = int(last.employee_id.replace("EMP", "")) + 1
        return f"EMP{num:03d}"

    @staticmethod
    def _get_or_create_skill(name: str) -> Skill:
        skill = Skill.query.filter(Skill.name.ilike(name)).first()
        if not skill:
            skill = Skill(name=name.strip())
            db.session.add(skill)
            db.session.flush()
        return skill

    @staticmethod
    def _validate(org_id, data: dict, current_emp_id: str = None) -> None:
        if not data.get("full_name"):
            raise EmployeeError("Full name is required.")
        if not data.get("email"):
            raise EmployeeError("Email is required.")
        if not validate_email(data["email"]):
            raise EmployeeError("Invalid email address.")
        if data.get("phone") and not validate_phone(data["phone"]):
            raise EmployeeError("Invalid phone number.")
        if data.get("department_id"):
            if not Department.query.filter_by(id=data["department_id"], org_id=org_id).first():
                raise EmployeeError("Department not found.")
        if data.get("manager_id"):
            if not Employee.query.filter_by(id=data["manager_id"], org_id=org_id).first():
                raise EmployeeError("Manager not found.")
        q = Employee.query.filter(
            Employee.org_id == org_id,
            Employee.email.ilike(data["email"])
        )
        if current_emp_id:
            q = q.filter(Employee.employee_id != current_emp_id.upper())
        if q.first():
            raise EmployeeError("Email already assigned to another employee.")

    @staticmethod
    def list_employees(org_id: str, filters: dict) -> list[dict]:
        q = Employee.query.filter_by(org_id=to_uuid(org_id))

        if filters.get("search"):
            like = f"%{filters['search'].lower()}%"
            q = q.filter(
                db.or_(
                    Employee.full_name.ilike(f"%{filters['search']}%"),
                    Employee.employee_id.ilike(f"%{filters['search']}%"),
                )
            )
        if filters.get("status"):
            q = q.filter_by(employment_status=filters["status"])
        if filters.get("employment_type"):
            q = q.filter_by(employment_type=filters["employment_type"])
        if filters.get("department"):
            q = q.join(Department).filter(Department.name.ilike(filters["department"]))

        emps = q.order_by(Employee.full_name).all()
        return [e.to_dict() for e in emps]

    @staticmethod
    def get_employee(org_id: str, employee_id: str) -> dict:
        emp = Employee.query.filter_by(
            org_id=to_uuid(org_id), employee_id=employee_id.upper()
        ).first()
        if not emp:
            raise EmployeeError(f"Employee '{employee_id}' not found.")
        return emp.to_dict()

    @staticmethod
    def create_employee(org_id: str, data: dict) -> dict:
        uid = to_uuid(org_id)
        EmployeeService._validate(uid, data)

        emp_id = data.get("employee_id") or EmployeeService._next_employee_id(uid)
        emp = Employee(
            org_id            = uid,
            employee_id       = emp_id.upper(),
            full_name         = data["full_name"],
            email             = data["email"].lower(),
            phone             = data.get("phone"),
            date_of_birth     = data.get("date_of_birth") or None,
            department_id     = data.get("department_id") or None,
            designation       = data.get("designation"),
            employment_type   = data.get("employment_type", "Full-Time"),
            joining_date      = data.get("joining_date") or None,
            employment_status = data.get("employment_status", "Active"),
            manager_id        = data.get("manager_id") or None,
            work_location     = data.get("work_location"),
            annual_ctc        = data.get("annual_ctc") or None,
        )
        db.session.add(emp)
        db.session.flush()   # get emp.id before setting skills

        if data.get("skills"):
            emp.skills = [EmployeeService._get_or_create_skill(s) for s in data["skills"] if s.strip()]

        db.session.commit()
        db.session.refresh(emp)
        return emp.to_dict()

    @staticmethod
    def update_employee(org_id: str, employee_id: str, data: dict) -> dict:
        uid = to_uuid(org_id)
        emp = Employee.query.filter_by(org_id=uid, employee_id=employee_id.upper()).first()
        if not emp:
            raise EmployeeError(f"Employee '{employee_id}' not found.")

        EmployeeService._validate(uid, data, current_emp_id=employee_id)

        emp.full_name         = data["full_name"]
        emp.email             = data["email"].lower()
        emp.phone             = data.get("phone")
        emp.date_of_birth     = data.get("date_of_birth") or None
        emp.department_id     = data.get("department_id") or None
        emp.designation       = data.get("designation")
        emp.employment_type   = data.get("employment_type", emp.employment_type)
        emp.joining_date      = data.get("joining_date") or None
        emp.employment_status = data.get("employment_status", emp.employment_status)
        emp.manager_id        = data.get("manager_id") or None
        emp.work_location     = data.get("work_location")
        emp.annual_ctc        = data.get("annual_ctc") or None

        if "skills" in data:
            emp.skills = [EmployeeService._get_or_create_skill(s) for s in data["skills"] if s.strip()]

        db.session.commit()
        db.session.refresh(emp)
        return emp.to_dict()

    @staticmethod
    def delete_employee(org_id: str, employee_id: str) -> None:
        emp = Employee.query.filter_by(
            org_id=to_uuid(org_id), employee_id=employee_id.upper()
        ).first()
        if not emp:
            raise EmployeeError(f"Employee '{employee_id}' not found.")
        db.session.delete(emp)
        db.session.commit()
