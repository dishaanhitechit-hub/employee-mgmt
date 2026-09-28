import datetime
from extensions import db, DictMixin, UUIDType


class Attendance(DictMixin, db.Model):
    __tablename__ = "attendances"
    __table_args__ = (
        db.UniqueConstraint("employee_id", "date", name="uq_attendance_emp_date"),
    )

    id          = db.Column(db.Integer,   primary_key=True)
    org_id      = db.Column(UUIDType,     db.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    employee_id = db.Column(db.Integer,   db.ForeignKey("employees.id",     ondelete="CASCADE"), nullable=False)
    date        = db.Column(db.Date,      nullable=False)
    check_in    = db.Column(db.Time,      nullable=True)
    check_out   = db.Column(db.Time,      nullable=True)
    # Present | Absent | Late | Half Day | On Leave | Holiday
    status      = db.Column(db.String(20), nullable=False, default="Present")
    notes       = db.Column(db.Text,      nullable=True)
    marked_by   = db.Column(UUIDType,     db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at  = db.Column(db.DateTime,  nullable=False, default=db.func.now())
    updated_at  = db.Column(db.DateTime,  nullable=False, default=db.func.now(), onupdate=db.func.now())

    employee  = db.relationship("Employee", backref=db.backref("attendances", lazy="dynamic"))
    marker    = db.relationship("User", foreign_keys=[marked_by])

    def to_dict(self) -> dict:
        d = super().to_dict()
        d["employee_name"]     = self.employee.full_name    if self.employee else None
        d["employee_code"]     = self.employee.employee_id  if self.employee else None
        d["department"]        = self.employee.department.name if (self.employee and self.employee.department) else None
        d["marked_by_name"]    = self.marker.full_name      if self.marker   else None
        # duration in minutes
        if self.check_in and self.check_out:
            ci = datetime.datetime.combine(datetime.date.today(), self.check_in)
            co = datetime.datetime.combine(datetime.date.today(), self.check_out)
            diff = (co - ci).seconds // 60
            d["duration_minutes"] = diff if diff >= 0 else None
        else:
            d["duration_minutes"] = None
        return d
