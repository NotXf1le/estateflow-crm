from __future__ import annotations

from crm.config import CSV_DEFINITIONS
from crm.models import Interaction
from crm.repositories.base_csv_repository import BaseCSVRepository


class InteractionsRepository(BaseCSVRepository[Interaction]):
    def __init__(self) -> None:
        super().__init__(CSV_DEFINITIONS["interactions"].path, Interaction)
