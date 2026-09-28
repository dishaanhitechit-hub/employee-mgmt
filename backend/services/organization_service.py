from extensions import db, to_uuid
from models.organization import Organization


class OrgError(Exception):
    pass


class OrganizationService:

    @staticmethod
    def list_all() -> list[dict]:
        return [o.to_dict() for o in Organization.query.order_by(Organization.name).all()]

    @staticmethod
    def get(org_id: str) -> dict:
        org = Organization.query.get(to_uuid(org_id))
        if not org:
            raise OrgError("Organization not found.")
        return org.to_dict()

    @staticmethod
    def create(name: str, domain: str, plan: str = "starter") -> dict:
        if Organization.query.filter_by(domain=domain).first():
            raise OrgError(f"Domain '{domain}' is already registered.")
        org = Organization(name=name, domain=domain, plan=plan)
        db.session.add(org)
        db.session.commit()
        return org.to_dict()

    @staticmethod
    def update(org_id: str, name: str, domain: str, plan: str, is_active: bool) -> dict:
        org = Organization.query.get(to_uuid(org_id))
        if not org:
            raise OrgError("Organization not found.")
        conflict = Organization.query.filter_by(domain=domain).first()
        if conflict and str(conflict.id) != org_id:
            raise OrgError(f"Domain '{domain}' is taken.")
        org.name = name
        org.domain = domain
        org.plan = plan
        org.is_active = is_active
        db.session.commit()
        return org.to_dict()
