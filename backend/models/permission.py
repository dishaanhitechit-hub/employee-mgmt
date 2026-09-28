from extensions import db, DictMixin


class RolePermission(DictMixin, db.Model):
    __tablename__ = "role_permissions"
    __table_args__ = (db.UniqueConstraint("role_id", "module_id", name="uq_rp_role_module"),)

    id         = db.Column(db.Integer, primary_key=True)
    role_id    = db.Column(db.Integer, db.ForeignKey("roles.id",   ondelete="CASCADE"), nullable=False)
    module_id  = db.Column(db.Integer, db.ForeignKey("modules.id", ondelete="CASCADE"), nullable=False)
    can_view   = db.Column(db.Boolean, nullable=False, default=False)
    can_create = db.Column(db.Boolean, nullable=False, default=False)
    can_edit   = db.Column(db.Boolean, nullable=False, default=False)
    can_delete = db.Column(db.Boolean, nullable=False, default=False)

    role   = db.relationship("Role",   back_populates="role_permissions")
    module = db.relationship("Module", back_populates="role_permissions")

    def to_rich_dict(self) -> dict:

        d = self.to_dict()
        d["module_code"]  = self.module.code
        d["module_label"] = self.module.label
        d["icon"]         = self.module.icon
        d["sort_order"]   = self.module.sort_order
        return d

    def __repr__(self):
        return f"<RolePermission role={self.role_id} module={self.module_id}>"
