from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.database import init_db
from app.tools import check_availability, create_appointment, lookup_appointment, query_services


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="Bologna TARI Voicebot — Tool Backend", lifespan=lifespan)


app.include_router(query_services.router, prefix="/tools")
app.include_router(check_availability.router, prefix="/tools")
app.include_router(create_appointment.router, prefix="/tools")
app.include_router(lookup_appointment.router, prefix="/tools")
