import uuid
from extensions import db, DictMixin, UUIDType


class Department(DictMixin, db.Model):
    __tablename__ = "departments"
    __table_args__ = (db.UniqueConstraint("org_id", "name", name="uq_dept_org_name"),)

    id          = db.Column(db.Integer, primary_key=True)
    org_id      = db.Column(UUIDType, db.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    name        = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    # head_id FK to employees — added after Employee is declared (use_alter avoids circular DDL)
    head_id     = db.Column(db.Integer, db.ForeignKey("employees.id", ondelete="SET NULL", use_alter=True, name="fk_dept_head"), nullable=True)

    # Relationships
    organization = db.relationship("Organization", back_populates="departments")
    head         = db.relationship("Employee", foreign_keys=[head_id], primaryjoin="Department.head_id == Employee.id", lazy="joined")
    employees    = db.relationship("Employee", foreign_keys="Employee.department_id", back_populates="department", lazy="dynamic")

    def to_dict(self) -> dict:
        d = super().to_dict()
        d["head_name"]        = self.head.full_name     if self.head else None
        d["head_designation"] = self.head.designation   if self.head else None
        d["employee_count"]   = self.employees.filter_by(employment_status="Active").count()
        return d

    def __repr__(self):
        return f"<Department {self.name}>"
