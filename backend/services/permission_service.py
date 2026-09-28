from models.module     import Module
from models.permission import RolePermission


class PermissionService:

    @staticmethod
    def list_modules() -> list[dict]:
        return [m.to_dict() for m in Module.query.order_by(Module.sort_order).all()]

    @staticmethod
    def get_user_permissions(role_id: int) -> dict:
        perms = RolePermission.query.filter_by(role_id=role_id).all()
        return {
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
