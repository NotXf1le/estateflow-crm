from __future__ import annotations

from crm.config import CSV_DEFINITIONS
from crm.models import Appointment
from crm.repositories.base_csv_repository import BaseCSVRepository


class AppointmentsRepository(BaseCSVRepository[Appointment]):
    def __init__(self) -> None:
        super().__init__(CSV_DEFINITIONS["appointments"].path, Appointment)
