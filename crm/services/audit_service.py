from __future__ import annotations

from crm.enums import AuditAction
from crm.models import AuditLog
from crm.repositories.audit_repository import AuditRepository
from crm.utils import generate_entity_id, now_iso


class AuditService:
    def __init__(self, repository: AuditRepository) -> None:
        self.repository = repository

    def log(
        self,
        *,
        actor_user_id: str,
        entity_type: str,
        entity_id: str,
        action: AuditAction | str,
        details: str,
    ) -> AuditLog:
        entry = AuditLog(
            audit_id=generate_entity_id("AUD"),
            actor_user_id=actor_user_id,
            entity_type=entity_type,
            entity_id=entity_id,
            action=str(action.value if hasattr(action, "value") else action),
            details=details,
            created_at=now_iso(),
        )
        return self.repository.create(entry)

    def recent(self, limit: int = 20) -> list[dict[str, str]]:
        rows = self.repository.all_dicts()
        rows.sort(key=lambda item: item.get("created_at", ""), reverse=True)
        return rows[:limit]
