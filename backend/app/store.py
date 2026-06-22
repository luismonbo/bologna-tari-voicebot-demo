from app.domain.booking import AppointmentStore

_store = AppointmentStore()


def get_store() -> AppointmentStore:
    return _store
