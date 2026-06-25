import hashlib
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Optional, Protocol, runtime_checkable


def make_idempotency_key(office: str, date: str, time: str, citizen_name: str) -> str:
    raw = f"{office}|{date}|{time}|{citizen_name}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


@dataclass
class Appointment:
    office: str
    date: str
    time: str
    citizen_name: str
    contact: str
    reason: Optional[str]
    confirmation_code: str
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


@runtime_checkable
class AppointmentStore(Protocol):
    """Persistence contract shared by every appointment store implementation.

    Both the in-memory and the SQLAlchemy-backed stores conform to this, so the
    tool endpoints depend on the abstraction rather than a concrete store. The
    shared contract is exercised in ``tests/test_store_contract.py`` against
    both implementations to keep them from drifting apart.
    """

    async def book(
        self,
        office: str,
        date: str,
        time: str,
        citizen_name: str,
        contact: str,
        reason: Optional[str],
    ) -> dict: ...

    async def lookup_by_name(self, citizen_name: str, date: Optional[str] = None) -> dict: ...

    async def booked_slots_for(self, office: str, date: str) -> set[str]: ...


class InMemoryAppointmentStore(AppointmentStore):
    """In-memory store used for fast unit tests and local runs without a DB."""

    def __init__(self):
        self._by_code: dict[str, Appointment] = {}
        self._slot_index: dict[tuple, str] = {}  # (office, date, time) → code

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

        if code in self._by_code:
            appt = self._by_code[code]
            return {"status": "confirmed", "confirmation_code": code, "appointment": asdict(appt)}

        slot_key = (office, date, time)
        if slot_key in self._slot_index:
            return {"status": "slot_unavailable", "slots": []}

        appt = Appointment(
            office=office,
            date=date,
            time=time,
            citizen_name=citizen_name,
            contact=contact,
            reason=reason,
            confirmation_code=code,
        )
        self._by_code[code] = appt
        self._slot_index[slot_key] = code
        return {"status": "confirmed", "confirmation_code": code, "appointment": asdict(appt)}

    def lookup_by_code(self, code: str) -> dict:
        appt = self._by_code.get(code)
        if appt is None:
            return {"status": "not_found", "appointment": None}
        return {"status": "found", "appointment": asdict(appt)}

    async def lookup_by_name(self, citizen_name: str, date: Optional[str] = None) -> dict:
        matches = [
            appt
            for appt in self._by_code.values()
            if appt.citizen_name.lower() == citizen_name.lower()
            and (date is None or appt.date == date)
        ]
        if not matches:
            return {"status": "not_found", "appointment": None}
        return {"status": "found", "appointment": asdict(matches[-1])}

    async def booked_slots_for(self, office: str, date: str) -> set[str]:
        return {
            appt.time
            for appt in self._by_code.values()
            if appt.office == office and appt.date == date
        }
