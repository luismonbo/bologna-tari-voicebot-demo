from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.domain import availability
from app.domain.dates import parse_iso_date, validate_future_date
from app.domain.booking import AppointmentStore
from app.store import get_store

router = APIRouter()


class AvailabilityRequest(BaseModel):
    office: str
    date: str


@router.post("/check_availability")
def check_availability(req: AvailabilityRequest, store: AppointmentStore = Depends(get_store)) -> dict:
    try:
        d = parse_iso_date(req.date)
        validate_future_date(d)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    office = req.office.lower()
    booked = store.booked_slots_for(office, req.date)
    return availability.check_availability(office, req.date, booked)
