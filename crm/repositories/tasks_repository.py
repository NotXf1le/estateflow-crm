from __future__ import annotations

from crm.config import CSV_DEFINITIONS
from crm.models import Task
from crm.repositories.base_csv_repository import BaseCSVRepository


class TasksRepository(BaseCSVRepository[Task]):
    def __init__(self) -> None:
        super().__init__(CSV_DEFINITIONS["tasks"].path, Task)
