from __future__ import annotations

from crm.config import CSV_DEFINITIONS
from crm.models import Property
from crm.repositories.base_csv_repository import BaseCSVRepository


class PropertiesRepository(BaseCSVRepository[Property]):
    def __init__(self) -> None:
        super().__init__(CSV_DEFINITIONS["properties"].path, Property)
