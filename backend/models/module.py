from extensions import db, DictMixin


class Module(DictMixin, db.Model):
    __tablename__ = "modules"

    id          = db.Column(db.Integer, primary_key=True)
    code        = db.Column(db.String(50), unique=True, nullable=False)
    label       = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    icon        = db.Column(db.String(50))
    sort_order  = db.Column(db.Integer, nullable=False, default=0)

    # Relationship
    role_permissions = db.relationship("RolePermission", back_populates="module", lazy="dynamic", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Module {self.code}>"
