from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.domain.dates import parse_iso_date, validate_future_date, parse_iso_time
from app.domain.booking import AppointmentStore
from app.store import get_store

router = APIRouter()


class CreateRequest(BaseModel):
    office: str
    date: str
    time: str
    citizen_name: str
    contact: str
    reason: Optional[str] = None


@router.post("/create_appointment")
def create_appointment(req: CreateRequest, store: AppointmentStore = Depends(get_store)) -> dict:
    try:
        d = parse_iso_date(req.date)
        validate_future_date(d)
        parse_iso_time(req.time)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    return store.book(
        office=req.office,
        date=req.date,
        time=req.time,
        citizen_name=req.citizen_name,
        contact=req.contact,
        reason=req.reason,
    )
