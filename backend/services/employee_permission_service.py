from extensions import db
from models.module                import Module
from models.permission            import RolePermission
from models.employee_permission   import EmployeePermission
from models.department_permission import DepartmentPermission
from models.employee              import Employee


class EmployeePermissionService:

    @staticmethod
    def get_employee_permissions(employee_id: int) -> dict:
        emp = Employee.query.get(employee_id)
        if not emp:
            raise ValueError("Employee not found.")

        modules = Module.query.order_by(Module.sort_order).all()

        role_perms = {}
        if emp.user_id:
            from models.user import User
            user = User.query.get(emp.user_id)
            if user:
                for p in RolePermission.query.filter_by(role_id=user.role_id).all():
                    role_perms[p.module_id] = p

        emp_perms = {
            p.module_id: p
            for p in EmployeePermission.query.filter_by(employee_id=employee_id).all()
        }

        dept_perms = {}
        if emp.department_id:
            for p in DepartmentPermission.query.filter_by(department_id=emp.department_id).all():
                dept_perms[p.module_id] = p

        result = []
        for m in modules:
            if m.id in dept_perms:
                p = dept_perms[m.id]
                source = "department"
            elif m.id in emp_perms:
                p = emp_perms[m.id]
                source = "employee"
            elif m.id in role_perms:
                p = role_perms[m.id]
                source = "role"
            else:
                p = None
                source = "none"

            result.append({
                "module_id":   m.id,
                "module_code": m.code,
                "module_label": m.label,
                "icon":        m.icon,
                "sort_order":  m.sort_order,
                "source":      source,
                "can_view":    p.can_view    if p else False,
                "can_create":  p.can_create  if p else False,
                "can_edit":    p.can_edit    if p else False,
                "can_delete":  p.can_delete  if p else False,
                "override": {
                    "can_view":   emp_perms[m.id].can_view    if m.id in emp_perms else None,
                    "can_create": emp_perms[m.id].can_create  if m.id in emp_perms else None,
                    "can_edit":   emp_perms[m.id].can_edit    if m.id in emp_perms else None,
                    "can_delete": emp_perms[m.id].can_delete  if m.id in emp_perms else None,
                } if m.id in emp_perms else None,
            })

        return {
            "employee_id":   emp.id,
            "employee_name": emp.full_name,
            "employee_code": emp.employee_id,
            "department":    emp.department.name if emp.department else None,
            "designation":   emp.designation,
            "permissions":   result,
        }

    @staticmethod
    def save_employee_permissions(employee_id: int, permissions: list) -> dict:
        emp = Employee.query.get(employee_id)
        if not emp:
            raise ValueError("Employee not found.")

        for item in permissions:
            mid = item["module_id"]
            existing = EmployeePermission.query.filter_by(
                employee_id=employee_id, module_id=mid
            ).first()

            all_false = not any([
                item.get("can_view"), item.get("can_create"),
                item.get("can_edit"), item.get("can_delete"),
            ])

            if all_false:
                if existing:
                    db.session.delete(existing)
            else:
                if existing:
                    existing.can_view   = item.get("can_view",   False)
                    existing.can_create = item.get("can_create", False)
                    existing.can_edit   = item.get("can_edit",   False)
                    existing.can_delete = item.get("can_delete", False)
                else:
                    db.session.add(EmployeePermission(
                        employee_id=employee_id,
                        module_id=mid,
                        can_view=item.get("can_view",   False),
                        can_create=item.get("can_create", False),
                        can_edit=item.get("can_edit",   False),
                        can_delete=item.get("can_delete", False),
                    ))

        db.session.commit()
        return EmployeePermissionService.get_employee_permissions(employee_id)

    @staticmethod
    def clear_employee_permissions(employee_id: int) -> None:
        EmployeePermission.query.filter_by(employee_id=employee_id).delete()
        db.session.commit()
