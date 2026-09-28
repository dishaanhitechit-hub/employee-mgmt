from extensions import db, DictMixin

# Association table — no extra columns so a plain Table is cleaner
employee_skills = db.Table(
    "employee_skills",
    db.Column("employee_id", db.Integer, db.ForeignKey("employees.id", ondelete="CASCADE"), primary_key=True),
    db.Column("skill_id",    db.Integer, db.ForeignKey("skills.id",    ondelete="CASCADE"), primary_key=True),
)


class Skill(DictMixin, db.Model):
    __tablename__ = "skills"

    id   = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    def __repr__(self):
        return f"<Skill {self.name}>"
