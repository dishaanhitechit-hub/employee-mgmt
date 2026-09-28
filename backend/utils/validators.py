import re


EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_RE = re.compile(r"^\+?[\d\s\-().]{7,20}$")


def validate_email(email: str) -> bool:
    return bool(EMAIL_RE.match(email or ""))


def validate_phone(phone: str) -> bool:
    return bool(PHONE_RE.match(phone or ""))


def require_fields(data: dict, fields: list[str]) -> list[str]:
    """Return list of missing required field names."""
    return [f for f in fields if not data.get(f)]


def clean_str(val) -> str | None:
    return val.strip() if isinstance(val, str) and val.strip() else None
