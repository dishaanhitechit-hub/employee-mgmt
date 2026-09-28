from extensions import db, DictMixin, UUIDType


class EmployeePermission(DictMixin, db.Model):
    __tablename__ = "employee_permissions"
    __table_args__ = (
        db.UniqueConstraint("employee_id", "module_id", name="uq_emp_perm"),
    )

    id          = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    module_id   = db.Column(db.Integer, db.ForeignKey("modules.id",   ondelete="CASCADE"), nullable=False)
    can_view    = db.Column(db.Boolean, nullable=False, default=False)
    can_create  = db.Column(db.Boolean, nullable=False, default=False)
    can_edit    = db.Column(db.Boolean, nullable=False, default=False)
    can_delete  = db.Column(db.Boolean, nullable=False, default=False)

    employee = db.relationship("Employee", backref=db.backref("permissions", lazy="dynamic", cascade="all, delete-orphan"))
    module   = db.relationship("Module")

    def to_rich_dict(self) -> dict:
        d = self.to_dict()
        d["module_code"]  = self.module.code
        d["module_label"] = self.module.label
        d["icon"]         = self.module.icon
        d["sort_order"]   = self.module.sort_order
        return d
