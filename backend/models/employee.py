import uuid
from extensions import db, DictMixin, UUIDType
from models.skill import employee_skills, Skill


class Employee(DictMixin, db.Model):
    __tablename__ = "employees"
    __table_args__ = (
        db.UniqueConstraint("org_id", "employee_id", name="uq_emp_org_empid"),
        db.UniqueConstraint("org_id", "email",       name="uq_emp_org_email"),
    )

    id                = db.Column(db.Integer,  primary_key=True)
    org_id            = db.Column(UUIDType, db.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    employee_id       = db.Column(db.String(20),   nullable=False)
    full_name         = db.Column(db.String(200),  nullable=False)
    email             = db.Column(db.String(200),  nullable=False)
    phone             = db.Column(db.String(20))
    date_of_birth     = db.Column(db.Date)
    department_id     = db.Column(db.Integer,      db.ForeignKey("departments.id", ondelete="SET NULL"), nullable=True)
    designation       = db.Column(db.String(150))
    employment_type   = db.Column(db.String(50))
    joining_date      = db.Column(db.Date)
    employment_status = db.Column(db.String(50),   default="Active")
    manager_id        = db.Column(db.Integer,      db.ForeignKey("employees.id", ondelete="SET NULL"), nullable=True)
    work_location     = db.Column(db.String(100))
    annual_ctc        = db.Column(db.Numeric(14, 2))
    user_id           = db.Column(UUIDType, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at        = db.Column(db.DateTime,     nullable=False, default=db.func.now())

    # Relationships
    organization = db.relationship("Organization", back_populates="employees")
    department   = db.relationship("Department",   foreign_keys=[department_id], back_populates="employees")
    skills       = db.relationship("Skill",        secondary=employee_skills, lazy="select")

    # Self-referential manager (defined outside class — see bottom of file)

    def to_dict(self) -> dict:
        d = super().to_dict()
        # Flatten department
        d["department"]    = self.department.name if self.department else None
        d["department_id"] = self.department_id
        # Flatten manager
        d["manager_name"]          = self.manager.full_name     if self.manager else None
        d["manager_employee_id"]   = self.manager.employee_id   if self.manager else None
        d["manager_designation"]   = self.manager.designation   if self.manager else None
        d["manager_db_id"]         = self.manager.id            if self.manager else None
        # Skills list
        d["skills"] = [s.name for s in self.skills]
        return d

    def __repr__(self):
        return f"<Employee {self.employee_id} {self.full_name}>"


Employee.manager = db.relationship(
    Employee,
    foreign_keys=[Employee.manager_id],
    primaryjoin=Employee.manager_id == Employee.id,
    remote_side=[Employee.id],
    uselist=False,
    lazy="joined",
)
