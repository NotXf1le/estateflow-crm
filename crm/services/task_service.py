from __future__ import annotations

from crm.repositories.clients_repository import ClientsRepository
from crm.repositories.deals_repository import DealsRepository
from crm.repositories.properties_repository import PropertiesRepository
from crm.repositories.tasks_repository import TasksRepository
from crm.repositories.users_repository import UsersRepository
from crm.services.audit_service import AuditService
from crm.services.base_service import BaseEntityService
from crm.utils import now_iso, today_iso
from crm.validators import ValidationError, validate_task_payload


class TaskService(BaseEntityService):
    entity_label = "Task"
    entity_type = "task"
    id_prefix = "TSK"
    search_fields = ("title", "priority", "status", "notes", "related_entity_id")
    sort_field = "due_date"

    def __init__(
        self,
        repository: TasksRepository,
        audit_service: AuditService,
        *,
        users_repository: UsersRepository,
        clients_repository: ClientsRepository,
        properties_repository: PropertiesRepository,
        deals_repository: DealsRepository,
    ) -> None:
        super().__init__(repository, audit_service)
        self.users_repository = users_repository
        self.clients_repository = clients_repository
        self.properties_repository = properties_repository
        self.deals_repository = deals_repository

    def _refresh_overdue_flags(self) -> None:
        changed = False
        records = self.repository.all()
        today = today_iso()
        for record in records:
            if record.status in {"done", "cancelled"}:
                continue
            if record.due_date and record.due_date < today and record.status != "overdue":
                record.status = "overdue"
                record.updated_at = now_iso()
                changed = True
        if changed:
            self.repository.save_all(records)

    def list_records(
        self,
        *,
        search_text: str = "",
        filters: dict[str, str] | None = None,
        sort_field: str | None = None,
        reverse: bool = False,
    ) -> list[dict[str, str]]:
        self._refresh_overdue_flags()
        return super().list_records(search_text=search_text, filters=filters, sort_field=sort_field, reverse=reverse)

    def validate_payload(self, payload: dict[str, str], *, record_id: str | None = None) -> dict[str, str]:
        normalized = validate_task_payload(payload)
        if not self.users_repository.exists(normalized["assigned_agent_id"]):
            raise ValidationError("Assigned agent does not exist.")
        entity_type = normalized["related_entity_type"]
        entity_id = normalized["related_entity_id"]
        if entity_type == "client" and entity_id and not self.clients_repository.exists(entity_id):
            raise ValidationError("Linked client does not exist.")
        if entity_type == "property" and entity_id and not self.properties_repository.exists(entity_id):
            raise ValidationError("Linked property does not exist.")
        if entity_type == "deal" and entity_id and not self.deals_repository.exists(entity_id):
            raise ValidationError("Linked deal does not exist.")
        if entity_type != "general" and not entity_id:
            raise ValidationError("Related entity id is required for non-general tasks.")
        return normalized

    def detail_sections(self, record_id: str) -> dict[str, list[str]]:
        task = self.repository.get(record_id)
        if not task:
            return {}
        agent = self.users_repository.get(task.assigned_agent_id)
        return {
            "Execution": [
                f"Assigned agent: {agent.full_name if agent else task.assigned_agent_id}",
                f"Due date: {task.due_date}",
                f"Priority: {task.priority}",
                f"Status: {task.status}",
                f"Related: {task.related_entity_type} / {task.related_entity_id or '-'}",
            ]
        }
