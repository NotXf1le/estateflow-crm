from __future__ import annotations

from crm.config import CSV_DEFINITIONS
from crm.models import AuditLog
from crm.repositories.base_csv_repository import BaseCSVRepository


class AuditRepository(BaseCSVRepository[AuditLog]):
    def __init__(self) -> None:
        super().__init__(CSV_DEFINITIONS["audit_log"].path, AuditLog)
