import os

import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AppointmentModel, SessionLocal

router = APIRouter()


async def get_db():
    async with SessionLocal() as session:
        yield session


@router.get("/appointments")
async def get_appointments(db: AsyncSession = Depends(get_db)):
    """Fetch all booked appointments."""
    query = select(AppointmentModel).order_by(AppointmentModel.date, AppointmentModel.time)
    result = await db.execute(query)
    appointments = result.scalars().all()

    return {
        "appointments": [
            {
                "office": a.office,
                "date": a.date,
                "time": a.time,
                "citizen_name": a.citizen_name,
                "contact": a.contact,
            }
            for a in appointments
        ]
    }


@router.get("/calls/recent")
async def get_recent_calls(limit: int = 10):
    """Fetch recent calls from Vapi API."""
    vapi_key = os.environ.get("VAPI_PRIVATE_API_KEY")
    if not vapi_key:
        raise HTTPException(status_code=500, detail="Vapi API key not configured")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.vapi.ai/call",
                headers={"Authorization": f"Bearer {vapi_key}"},
                params={"limit": limit},
            )
            response.raise_for_status()

            calls_data = response.json()
            calls = calls_data.get("calls", [])

            return {
                "calls": [
                    {
                        "id": call.get("id"),
                        "timestamp": call.get("createdAt"),
                        "duration": call.get("duration", 0),
                        "citizen_name": call.get("customer", {}).get("name"),
                        "result": determine_call_result(call),
                    }
                    for call in calls
                ]
            }
    except httpx.HTTPError as e:
        detail = f"Failed to fetch calls from Vapi: {str(e)}"
        raise HTTPException(status_code=502, detail=detail)


@router.get("/call/{call_id}/transcript")
async def get_call_transcript(call_id: str):
    """Fetch transcript for a specific call from Vapi API."""
    vapi_key = os.environ.get("VAPI_PRIVATE_API_KEY")
    if not vapi_key:
        raise HTTPException(status_code=500, detail="Vapi API key not configured")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.vapi.ai/call/{call_id}",
                headers={"Authorization": f"Bearer {vapi_key}"},
            )
            response.raise_for_status()

            call_data = response.json()
            messages = call_data.get("messages", [])

            transcript = []
            for msg in messages:
                role = "citizen" if msg.get("role") == "user" else "assistant"
                text = msg.get("content", "")
                if text:
                    transcript.append({"role": role, "text": text})

            return {
                "transcript": transcript,
                "metadata": {
                    "duration": call_data.get("duration", 0),
                    "timestamp": call_data.get("createdAt"),
                    "citizen_name": call_data.get("customer", {}).get("name"),
                },
            }
    except httpx.HTTPError as e:
        detail = f"Failed to fetch transcript from Vapi: {str(e)}"
        raise HTTPException(status_code=502, detail=detail)


def determine_call_result(call: dict) -> str:
    """Determine call result based on call data."""
    if "appointment" in call and call.get("appointment"):
        return "booked"
    if call.get("status") == "completed":
        return "info"
    return "error"
