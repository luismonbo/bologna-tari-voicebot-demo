from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.domain.booking import AppointmentStore
from app.store import get_store

router = APIRouter()


class LookupRequest(BaseModel):
    citizen_name: str
    date: Optional[str] = None


@router.post("/lookup_appointment")
async def lookup_appointment(
    req: LookupRequest, store: AppointmentStore = Depends(get_store)
) -> dict:
    # Case-normalization is the store's responsibility (see AppointmentStore).
    return await store.lookup_by_name(req.citizen_name, date=req.date)
