from __future__ import annotations

from crm.config import CSV_DEFINITIONS
from crm.models import Deal
from crm.repositories.base_csv_repository import BaseCSVRepository


class DealsRepository(BaseCSVRepository[Deal]):
    def __init__(self) -> None:
        super().__init__(CSV_DEFINITIONS["deals"].path, Deal)
