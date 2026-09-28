from datetime import timedelta

from flask_jwt_extended import create_access_token, create_refresh_token

from config import JWT_ACCESS_EX, JWT_REFRESH_EX
from extensions import db, to_uuid
from models.user         import User
from models.organization import Organization
from models.role         import Role
from models.permission   import RolePermission
from models.employee     import Employee


class AuthError(Exception):
    pass


class AuthService:

    @staticmethod
    def login(email: str, password: str) -> dict:
        user = User.query.filter(User.email.ilike(email)).first()
        if not user:
            raise AuthError("Invalid email or password.")
        if not user.is_active:
            raise AuthError("Your account is inactive. Contact HR.")
        if not user.check_password(password):
            raise AuthError("Invalid email or password.")

        org = Organization.query.get(user.org_id)
        if not org or not org.is_active:
            raise AuthError("Organization is inactive.")

        role  = user.role
        perms = RolePermission.query.filter_by(role_id=user.role_id).all()

        # Link to employee record if one exists for this user
        linked_emp = Employee.query.filter_by(org_id=user.org_id, user_id=user.id).first()
        emp_id  = linked_emp.id            if linked_emp else None
        dept_id = linked_emp.department_id if linked_emp else None

        claims = {
            "org_id":        str(user.org_id),
            "role_id":       user.role_id,
            "role_code":     role.code,
            "email":         user.email,
            "full_name":     user.full_name,
            "employee_id":   emp_id,
            "department_id": dept_id,
        }
        access_token  = create_access_token(
            identity=str(user.id),
            additional_claims=claims,
            expires_delta=timedelta(minutes=JWT_ACCESS_EX),
        )
        refresh_token = create_refresh_token(
            identity=str(user.id),
            expires_delta=timedelta(days=JWT_REFRESH_EX),
        )

        user.last_login = db.func.now()
        db.session.commit()

        perm_map = {
            p.module.code: {
                "can_view":   p.can_view,
                "can_create": p.can_create,
                "can_edit":   p.can_edit,
                "can_delete": p.can_delete,
                "label":      p.module.label,
                "icon":       p.module.icon,
            }
            for p in perms
        }

        return {
            "access_token":  access_token,
            "refresh_token": refresh_token,
            "user": {
                "id":        str(user.id),
                "email":     user.email,
                "full_name": user.full_name,
                "org_id":    str(user.org_id),
                "org_name":  org.name,
                "role_code": role.code,
                "role_name": role.name,
            },
            "permissions": perm_map,
        }

    @staticmethod
    def refresh_tokens(user_id: str) -> str:
        user = User.query.get(to_uuid(user_id))
        if not user or not user.is_active:
            raise AuthError("User not found or inactive.")
        role = user.role
        linked_emp = Employee.query.filter_by(org_id=user.org_id, user_id=user.id).first()
        claims = {
            "org_id":        str(user.org_id),
            "role_id":       user.role_id,
            "role_code":     role.code,
            "email":         user.email,
            "full_name":     user.full_name,
            "employee_id":   linked_emp.id            if linked_emp else None,
            "department_id": linked_emp.department_id if linked_emp else None,
        }
        return create_access_token(
            identity=str(user.id),
            additional_claims=claims,
            expires_delta=timedelta(minutes=JWT_ACCESS_EX),
        )
