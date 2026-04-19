from __future__ import annotations

from crm.config import CSV_DEFINITIONS
from crm.models import Client
from crm.repositories.base_csv_repository import BaseCSVRepository


class ClientsRepository(BaseCSVRepository[Client]):
    def __init__(self) -> None:
        super().__init__(CSV_DEFINITIONS["clients"].path, Client)
