from extensions import db, DictMixin


class DepartmentPermission(DictMixin, db.Model):
    __tablename__ = "department_permissions"
    __table_args__ = (
        db.UniqueConstraint("department_id", "module_id", name="uq_dept_perm"),
    )

    id            = db.Column(db.Integer, primary_key=True)
    department_id = db.Column(db.Integer, db.ForeignKey("departments.id", ondelete="CASCADE"), nullable=False)
    module_id     = db.Column(db.Integer, db.ForeignKey("modules.id",     ondelete="CASCADE"), nullable=False)
    can_view      = db.Column(db.Boolean, nullable=False, default=False)
    can_create    = db.Column(db.Boolean, nullable=False, default=False)
    can_edit      = db.Column(db.Boolean, nullable=False, default=False)
    can_delete    = db.Column(db.Boolean, nullable=False, default=False)

    department = db.relationship("Department", backref=db.backref("permissions", lazy="dynamic", cascade="all, delete-orphan"))
    module     = db.relationship("Module")

    def to_rich_dict(self) -> dict:
        d = self.to_dict()
        d["module_code"]  = self.module.code
        d["module_label"] = self.module.label
        d["icon"]         = self.module.icon
        d["sort_order"]   = self.module.sort_order
        return d
