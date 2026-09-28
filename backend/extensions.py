import uuid
import datetime
from decimal import Decimal

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.types import TypeDecorator, String

db = SQLAlchemy()


class UUIDType(TypeDecorator):
    impl = String(36)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return str(value) if isinstance(value, uuid.UUID) else str(uuid.UUID(str(value)))

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return uuid.UUID(value) if not isinstance(value, uuid.UUID) else value


def to_uuid(val) -> uuid.UUID:
    return val if isinstance(val, uuid.UUID) else uuid.UUID(val)


class DictMixin:
    def to_dict(self) -> dict:
        result = {}
        for col in self.__table__.columns:
            val = getattr(self, col.name)
            if isinstance(val, uuid.UUID):
                result[col.name] = str(val)
            elif isinstance(val, datetime.datetime):
                result[col.name] = val.isoformat()
            elif isinstance(val, datetime.date):
                result[col.name] = val.isoformat()
            elif isinstance(val, Decimal):
                result[col.name] = float(val)
            else:
                result[col.name] = val
        return result
