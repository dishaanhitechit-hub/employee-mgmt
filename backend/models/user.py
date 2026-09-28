import uuid
import bcrypt
from extensions import db, DictMixin, UUIDType


class User(DictMixin, db.Model):
    __tablename__ = "users"
    __table_args__ = (db.UniqueConstraint("org_id", "email", name="uq_user_org_email"),)

    id            = db.Column(UUIDType, primary_key=True, default=uuid.uuid4)
    org_id        = db.Column(UUIDType, db.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    role_id       = db.Column(db.Integer,         db.ForeignKey("roles.id"),                            nullable=False)
    email         = db.Column(db.String(200),     nullable=False)
    password_hash = db.Column(db.String(255),     nullable=False)
    full_name     = db.Column(db.String(200),     nullable=False)
    is_active     = db.Column(db.Boolean,         nullable=False, default=True)
    last_login    = db.Column(db.DateTime)
    created_at    = db.Column(db.DateTime,        nullable=False, default=db.func.now())

    # Relationships
    organization = db.relationship("Organization", back_populates="users")
    role         = db.relationship("Role",         back_populates="users")

    def set_password(self, plain: str) -> None:
        self.password_hash = bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()

    def check_password(self, plain: str) -> bool:
        return bcrypt.checkpw(plain.encode(), self.password_hash.encode())

    def to_dict(self) -> dict:
        d = super().to_dict()
        d.pop("password_hash", None)
        d["role_name"] = self.role.name if self.role else None
        d["role_code"] = self.role.code if self.role else None
        return d

    def __repr__(self):
        return f"<User {self.email}>"
