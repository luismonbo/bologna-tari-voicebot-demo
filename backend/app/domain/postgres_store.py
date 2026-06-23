from dataclasses import asdict
from datetime import datetime, UTC
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import AppointmentModel
from app.domain.booking import Appointment, make_idempotency_key


class PostgresAppointmentStore:
    def __init__(self, session: Session):
        self.session = session

    def book(
        self,
        office: str,
        date: str,
        time: str,
        citizen_name: str,
        contact: str,
        reason: Optional[str],
    ) -> dict:
        code = make_idempotency_key(office, date, time, citizen_name)

        existing = self.session.query(AppointmentModel).filter_by(code=code).first()
        if existing:
            appt = self._model_to_appointment(existing)
            return {"status": "confirmed", "confirmation_code": code, "appointment": asdict(appt)}

        model = AppointmentModel(
            code=code,
            office=office,
            date=date,
            time=time,
            citizen_name=citizen_name,
            contact=contact,
            reason=reason,
            created_at=datetime.now(UTC),
        )
        self.session.add(model)

        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            return {"status": "slot_unavailable", "slots": []}

        appt = self._model_to_appointment(model)
        return {"status": "confirmed", "confirmation_code": code, "appointment": asdict(appt)}

    def lookup_by_code(self, code: str) -> dict:
        model = self.session.query(AppointmentModel).filter_by(code=code).first()
        if model is None:
            return {"status": "not_found", "appointment": None}
        appt = self._model_to_appointment(model)
        return {"status": "found", "appointment": asdict(appt)}

    def lookup_by_name(self, citizen_name: str, date: Optional[str] = None) -> dict:
        query = self.session.query(AppointmentModel).filter(
            AppointmentModel.citizen_name.ilike(citizen_name)
        )
        if date:
            query = query.filter_by(date=date)

        matches = query.all()
        if not matches:
            return {"status": "not_found", "appointment": None}

        latest = max(matches, key=lambda m: m.created_at)
        appt = self._model_to_appointment(latest)
        return {"status": "found", "appointment": asdict(appt)}

    def booked_slots_for(self, office: str, date: str) -> set[str]:
        models = self.session.query(AppointmentModel).filter_by(office=office, date=date).all()
        return {m.time for m in models}

    @staticmethod
    def _model_to_appointment(model: AppointmentModel) -> Appointment:
        return Appointment(
            office=model.office,
            date=model.date,
            time=model.time,
            citizen_name=model.citizen_name,
            contact=model.contact,
            reason=model.reason,
            confirmation_code=model.code,
            created_at=model.created_at.isoformat(),
        )