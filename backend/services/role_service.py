from extensions import db, to_uuid
from models.role       import Role
from models.permission import RolePermission
from models.module     import Module


class RoleError(Exception):
    pass


class RoleService:

    @staticmethod
    def _serialize(role: Role) -> dict:
        d = role.to_dict()
        d["permissions"] = [p.to_rich_dict() for p in role.role_permissions]
        d["user_count"]  = role.user_count()
        return d

    @staticmethod
    def list_roles(org_id: str) -> list[dict]:
        roles = Role.query.filter_by(org_id=to_uuid(org_id)).order_by(Role.name).all()
        return [RoleService._serialize(r) for r in roles]

    @staticmethod
    def get_role(org_id: str, role_id: int) -> dict:
        role = Role.query.filter_by(id=role_id, org_id=to_uuid(org_id)).first()
        if not role:
            raise RoleError("Role not found.")
        return RoleService._serialize(role)

    @staticmethod
    def create_role(org_id: str, name: str, code: str, description: str = None) -> dict:
        if not name or not code:
            raise RoleError("name and code are required.")
        if Role.query.filter_by(org_id=to_uuid(org_id), code=code).first():
            raise RoleError(f"Role code '{code}' already exists.")
        role = Role(org_id=to_uuid(org_id), name=name, code=code, description=description)
        db.session.add(role)
        db.session.commit()
        return RoleService._serialize(role)

    @staticmethod
    def update_role(org_id: str, role_id: int, name: str, description: str) -> dict:
        role = Role.query.filter_by(id=role_id, org_id=to_uuid(org_id)).first()
        if not role:
            raise RoleError("Role not found.")
        if role.is_system and not name:
            raise RoleError("System roles require a name.")
        role.name = name
        role.description = description
        db.session.commit()
        return RoleService._serialize(role)

    @staticmethod
    def delete_role(org_id: str, role_id: int) -> None:
        role = Role.query.filter_by(id=role_id, org_id=to_uuid(org_id)).first()
        if not role:
            raise RoleError("Role not found.")
        if role.is_system:
            raise RoleError("Cannot delete a system role.")
        if role.user_count() > 0:
            raise RoleError("Cannot delete role: users are assigned to it.")
        db.session.delete(role)
        db.session.commit()

    @staticmethod
    def set_permissions(org_id: str, role_id: int, permissions: list[dict]) -> dict:
        role = Role.query.filter_by(id=role_id, org_id=to_uuid(org_id)).first()
        if not role:
            raise RoleError("Role not found.")
        # Validate module ids
        for p in permissions:
            if not Module.query.get(p["module_id"]):
                raise RoleError(f"Module id {p['module_id']} not found.")
        # Delete old, insert new
        RolePermission.query.filter_by(role_id=role_id).delete()
        for p in permissions:
            rp = RolePermission(
                role_id    = role_id,
                module_id  = p["module_id"],
                can_view   = bool(p.get("can_view")),
                can_create = bool(p.get("can_create")),
                can_edit   = bool(p.get("can_edit")),
                can_delete = bool(p.get("can_delete")),
            )
            db.session.add(rp)
        db.session.commit()
        db.session.refresh(role)
        return RoleService._serialize(role)
