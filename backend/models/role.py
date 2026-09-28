import uuid
from extensions import db, DictMixin, UUIDType


class Role(DictMixin, db.Model):
    __tablename__ = "roles"
    __table_args__ = (db.UniqueConstraint("org_id", "code", name="uq_role_org_code"),)

    id          = db.Column(db.Integer, primary_key=True)
    org_id      = db.Column(UUIDType, db.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    name        = db.Column(db.String(100), nullable=False)
    code        = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    is_system   = db.Column(db.Boolean, nullable=False, default=False)
    created_at  = db.Column(db.DateTime, nullable=False, default=db.func.now())

    # Relationships
    organization     = db.relationship("Organization", back_populates="roles")
    users            = db.relationship("User", back_populates="role", lazy="dynamic")
    role_permissions = db.relationship("RolePermission", back_populates="role", lazy="select", cascade="all, delete-orphan")

    def user_count(self) -> int:
        return self.users.count()

    def __repr__(self):
        return f"<Role {self.code}>"
