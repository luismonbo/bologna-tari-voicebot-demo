from dataclasses import asdict
from datetime import datetime, UTC
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.database import AppointmentModel
from app.domain.booking import Appointment, make_idempotency_key


class PostgresAppointmentStore:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def book(
        self,
        office: str,
        date: str,
        time: str,
        citizen_name: str,
        contact: str,
        reason: Optional[str],
    ) -> dict:
        code = make_idempotency_key(office, date, time, citizen_name)

        stmt = select(AppointmentModel).where(AppointmentModel.code == code)
        result = await self.session.execute(stmt)
        existing = result.scalar_one_or_none()

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
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            return {"status": "slot_unavailable", "slots": []}

        appt = self._model_to_appointment(model)
        return {"status": "confirmed", "confirmation_code": code, "appointment": asdict(appt)}

    async def lookup_by_code(self, code: str) -> dict:
        stmt = select(AppointmentModel).where(AppointmentModel.code == code)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return {"status": "not_found", "appointment": None}
        appt = self._model_to_appointment(model)
        return {"status": "found", "appointment": asdict(appt)}

    async def lookup_by_name(self, citizen_name: str, date: Optional[str] = None) -> dict:
        stmt = select(AppointmentModel).where(
            AppointmentModel.citizen_name.ilike(citizen_name)
        )
        if date:
            stmt = stmt.where(AppointmentModel.date == date)

        result = await self.session.execute(stmt)
        matches = result.scalars().all()

        if not matches:
            return {"status": "not_found", "appointment": None}

        latest = max(matches, key=lambda m: m.created_at)
        appt = self._model_to_appointment(latest)
        return {"status": "found", "appointment": asdict(appt)}

    async def booked_slots_for(self, office: str, date: str) -> set[str]:
        stmt = select(AppointmentModel).where(
            AppointmentModel.office == office,
            AppointmentModel.date == date
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
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