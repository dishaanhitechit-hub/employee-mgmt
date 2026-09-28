from extensions import db, to_uuid
from models.user import User
from models.role import Role


class UserError(Exception):
    pass


class UserService:

    @staticmethod
    def list_users(org_id: str) -> list[dict]:
        users = (
            User.query
            .filter_by(org_id=to_uuid(org_id))
            .order_by(User.full_name)
            .all()
        )
        return [u.to_dict() for u in users]

    @staticmethod
    def get_user(org_id: str, user_id: str) -> dict:
        user = User.query.filter_by(id=to_uuid(user_id), org_id=to_uuid(org_id)).first()
        if not user:
            raise UserError("User not found.")
        return user.to_dict()

    @staticmethod
    def create_user(org_id: str, role_id: int, email: str, password: str, full_name: str) -> dict:
        if not email or not role_id or not password or not full_name:
            raise UserError("full_name, email, password, and role_id are required.")
        if len(password) < 8:
            raise UserError("Password must be at least 8 characters.")
        existing = User.query.filter(
            User.org_id == to_uuid(org_id), User.email.ilike(email)
        ).first()
        if existing:
            raise UserError(f"Email '{email}' already exists in this organisation.")
        role = Role.query.filter_by(id=role_id, org_id=to_uuid(org_id)).first()
        if not role:
            raise UserError("Role not found.")
        user = User(org_id=to_uuid(org_id), role_id=role_id, email=email.lower(), full_name=full_name)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user.to_dict()

    @staticmethod
    def update_user(org_id: str, user_id: str, fields: dict) -> dict:
        user = User.query.filter_by(id=to_uuid(user_id), org_id=to_uuid(org_id)).first()
        if not user:
            raise UserError("User not found.")
        if "role_id" in fields:
            role = Role.query.filter_by(id=fields["role_id"], org_id=to_uuid(org_id)).first()
            if not role:
                raise UserError("Role not found.")
            user.role_id = fields["role_id"]
        if "full_name" in fields:
            user.full_name = fields["full_name"]
        if "is_active" in fields:
            user.is_active = bool(fields["is_active"])
        db.session.commit()
        return user.to_dict()

    @staticmethod
    def change_password(org_id: str, user_id: str, current: str, new_pwd: str) -> None:
        user = User.query.filter_by(id=to_uuid(user_id), org_id=to_uuid(org_id)).first()
        if not user:
            raise UserError("User not found.")
        if not user.check_password(current):
            raise UserError("Current password is incorrect.")
        if len(new_pwd) < 8:
            raise UserError("New password must be at least 8 characters.")
        user.set_password(new_pwd)
        db.session.commit()

    @staticmethod
    def delete_user(org_id: str, user_id: str) -> None:
        user = User.query.filter_by(id=to_uuid(user_id), org_id=to_uuid(org_id)).first()
        if not user:
            raise UserError("User not found.")
        db.session.delete(user)
        db.session.commit()
