import datetime
from extensions import db, to_uuid
from models.attendance import Attendance
from models.employee   import Employee


class AttendanceError(Exception):
    pass


class AttendanceService:

    @staticmethod
    def _parse_date(val) -> datetime.date:
        if isinstance(val, datetime.date):
            return val
        try:
            return datetime.date.fromisoformat(str(val))
        except Exception:
            raise AttendanceError(f"Invalid date '{val}'. Use YYYY-MM-DD.")

    @staticmethod
    def _parse_time(val):
        if val is None:
            return None
        if isinstance(val, datetime.time):
            return val
        try:
            return datetime.time.fromisoformat(str(val))
        except Exception:
            raise AttendanceError(f"Invalid time '{val}'. Use HH:MM or HH:MM:SS.")

    @staticmethod
    def list_attendance(org_id: str, filters: dict) -> list[dict]:
        uid = to_uuid(org_id)
        q = Attendance.query.filter_by(org_id=uid)

        if filters.get("employee_id"):
            q = q.filter_by(employee_id=int(filters["employee_id"]))

        if filters.get("date_from"):
            q = q.filter(Attendance.date >= AttendanceService._parse_date(filters["date_from"]))

        if filters.get("date_to"):
            q = q.filter(Attendance.date <= AttendanceService._parse_date(filters["date_to"]))

        if filters.get("status"):
            q = q.filter_by(status=filters["status"])

        if filters.get("department_id"):
            q = q.join(Employee).filter(Employee.department_id == int(filters["department_id"]))

        return [a.to_dict() for a in q.order_by(Attendance.date.desc(), Attendance.employee_id).all()]

    @staticmethod
    def get_attendance(org_id: str, attendance_id: int) -> dict:
        a = Attendance.query.filter_by(org_id=to_uuid(org_id), id=attendance_id).first()
        if not a:
            raise AttendanceError("Attendance record not found.")
        return a.to_dict()

    @staticmethod
    def mark_attendance(org_id: str, data: dict, marked_by_user_id: str) -> dict:
        uid = to_uuid(org_id)

        emp_id = data.get("employee_id")
        if not emp_id:
            raise AttendanceError("employee_id is required.")
        emp = Employee.query.filter_by(org_id=uid, id=int(emp_id)).first()
        if not emp:
            raise AttendanceError("Employee not found in this organisation.")

        date = AttendanceService._parse_date(data.get("date") or datetime.date.today())

        status = data.get("status", "Present")
        valid_statuses = {"Present", "Absent", "Late", "Half Day", "On Leave", "Holiday"}
        if status not in valid_statuses:
            raise AttendanceError(f"Invalid status. Choose from: {', '.join(sorted(valid_statuses))}")

        check_in  = AttendanceService._parse_time(data.get("check_in"))
        check_out = AttendanceService._parse_time(data.get("check_out"))

        if check_in and check_out and check_out <= check_in:
            raise AttendanceError("check_out must be after check_in.")

        existing = Attendance.query.filter_by(org_id=uid, employee_id=emp.id, date=date).first()
        if existing:
            existing.status     = status
            existing.check_in   = check_in
            existing.check_out  = check_out
            existing.notes      = data.get("notes")
            existing.marked_by  = marked_by_user_id
            existing.updated_at = db.func.now()
            record = existing
        else:
            record = Attendance(
                org_id=uid, employee_id=emp.id, date=date,
                status=status, check_in=check_in, check_out=check_out,
                notes=data.get("notes"), marked_by=marked_by_user_id,
            )
            db.session.add(record)

        db.session.commit()
        db.session.refresh(record)
        return record.to_dict()

    @staticmethod
    def bulk_mark(org_id: str, date_str: str, records: list, marked_by_user_id: str) -> list[dict]:
        results = []
        for item in records:
            item["date"] = date_str
            results.append(AttendanceService.mark_attendance(org_id, item, marked_by_user_id))
        return results

    @staticmethod
    def update_attendance(org_id: str, attendance_id: int, data: dict, marked_by_user_id: str) -> dict:
        a = Attendance.query.filter_by(org_id=to_uuid(org_id), id=attendance_id).first()
        if not a:
            raise AttendanceError("Attendance record not found.")

        if "status" in data:
            valid_statuses = {"Present", "Absent", "Late", "Half Day", "On Leave", "Holiday"}
            if data["status"] not in valid_statuses:
                raise AttendanceError(f"Invalid status.")
            a.status = data["status"]

        if "check_in"  in data: a.check_in  = AttendanceService._parse_time(data["check_in"])
        if "check_out" in data: a.check_out = AttendanceService._parse_time(data["check_out"])
        if "notes"     in data: a.notes     = data["notes"]
        a.marked_by = marked_by_user_id

        db.session.commit()
        db.session.refresh(a)
        return a.to_dict()

    @staticmethod
    def delete_attendance(org_id: str, attendance_id: int) -> None:
        a = Attendance.query.filter_by(org_id=to_uuid(org_id), id=attendance_id).first()
        if not a:
            raise AttendanceError("Attendance record not found.")
        db.session.delete(a)
        db.session.commit()

    @staticmethod
    def summary(org_id: str, filters: dict) -> dict:
        uid = to_uuid(org_id)
        q = Attendance.query.filter_by(org_id=uid)

        if filters.get("employee_id"):
            q = q.filter_by(employee_id=int(filters["employee_id"]))
        if filters.get("date_from"):
            q = q.filter(Attendance.date >= AttendanceService._parse_date(filters["date_from"]))
        if filters.get("date_to"):
            q = q.filter(Attendance.date <= AttendanceService._parse_date(filters["date_to"]))

        records = q.all()
        counts = {}
        for r in records:
            counts[r.status] = counts.get(r.status, 0) + 1

        return {
            "total":    len(records),
            "present":  counts.get("Present",  0),
            "absent":   counts.get("Absent",   0),
            "late":     counts.get("Late",      0),
            "half_day": counts.get("Half Day",  0),
            "on_leave": counts.get("On Leave",  0),
            "holiday":  counts.get("Holiday",   0),
        }
