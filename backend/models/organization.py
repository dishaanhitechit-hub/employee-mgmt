import uuid
from extensions import db, DictMixin, UUIDType


class Organization(DictMixin, db.Model):
    __tablename__ = "organizations"

    id         = db.Column(UUIDType, primary_key=True, default=uuid.uuid4)
    name       = db.Column(db.String(200), nullable=False)
    domain     = db.Column(db.String(200), unique=True, nullable=False)
    plan       = db.Column(db.String(50), nullable=False, default="starter")
    is_active  = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())

    # Relationships
    roles       = db.relationship("Role",       back_populates="organization", lazy="dynamic", cascade="all, delete-orphan")
    users       = db.relationship("User",       back_populates="organization", lazy="dynamic", cascade="all, delete-orphan")
    departments = db.relationship("Department", back_populates="organization", lazy="dynamic", cascade="all, delete-orphan")
    employees   = db.relationship("Employee",   back_populates="organization", lazy="dynamic", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Organization {self.name}>"
