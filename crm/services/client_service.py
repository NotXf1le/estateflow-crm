from __future__ import annotations

from crm.repositories.appointments_repository import AppointmentsRepository
from crm.repositories.clients_repository import ClientsRepository
from crm.repositories.deals_repository import DealsRepository
from crm.repositories.interactions_repository import InteractionsRepository
from crm.repositories.properties_repository import PropertiesRepository
from crm.repositories.tasks_repository import TasksRepository
from crm.repositories.users_repository import UsersRepository
from crm.services.audit_service import AuditService
from crm.services.base_service import BaseEntityService
from crm.validators import ValidationError, validate_client_payload


class ClientService(BaseEntityService):
    entity_label = "Client"
    entity_type = "client"
    id_prefix = "CLI"
    search_fields = ("full_name", "phone", "email", "preferred_city", "notes")
    sort_field = "full_name"

    def __init__(
        self,
        repository: ClientsRepository,
        audit_service: AuditService,
        *,
        users_repository: UsersRepository,
        properties_repository: PropertiesRepository,
        deals_repository: DealsRepository,
        appointments_repository: AppointmentsRepository,
        tasks_repository: TasksRepository,
        interactions_repository: InteractionsRepository,
    ) -> None:
        super().__init__(repository, audit_service)
        self.users_repository = users_repository
        self.properties_repository = properties_repository
        self.deals_repository = deals_repository
        self.appointments_repository = appointments_repository
        self.tasks_repository = tasks_repository
        self.interactions_repository = interactions_repository

    def validate_payload(self, payload: dict[str, str], *, record_id: str | None = None) -> dict[str, str]:
        normalized = validate_client_payload(payload)
        agent_id = normalized.get("assigned_agent_id", "")
        if agent_id and not self.users_repository.exists(agent_id):
            raise ValidationError("Assigned agent does not exist.")
        return normalized

    def dependency_error(self, record_id: str) -> str | None:
        referenced = []
        if any(item.owner_client_id == record_id for item in self.properties_repository.all()):
            referenced.append("property ownership")
        if any(item.client_id == record_id for item in self.deals_repository.all()):
            referenced.append("deals")
        if any(item.client_id == record_id for item in self.appointments_repository.all()):
            referenced.append("appointments")
        if any(item.client_id == record_id for item in self.interactions_repository.all()):
            referenced.append("interactions")
        if any(item.related_entity_type == "client" and item.related_entity_id == record_id for item in self.tasks_repository.all()):
            referenced.append("tasks")
        if referenced:
            return f"Client cannot be deleted because it is still referenced by: {', '.join(sorted(set(referenced)))}."
        return None

    def detail_sections(self, record_id: str) -> dict[str, list[str]]:
        client = self.repository.get(record_id)
        if not client:
            return {}
        agent = self.users_repository.get(client.assigned_agent_id) if client.assigned_agent_id else None
        return {
            "Overview": [
                f"Role: {client.role_type}",
                f"Status: {client.status}",
                f"Assigned agent: {agent.full_name if agent else '-'}",
                f"Budget: {client.budget_min or '-'} to {client.budget_max or '-'} EUR",
                f"Preferred city: {client.preferred_city or '-'}",
            ],
            "Activity": [
                f"Deals: {len([item for item in self.deals_repository.all() if item.client_id == record_id])}",
                f"Appointments: {len([item for item in self.appointments_repository.all() if item.client_id == record_id])}",
                f"Tasks: {len([item for item in self.tasks_repository.all() if item.related_entity_type == 'client' and item.related_entity_id == record_id])}",
                f"Interactions: {len([item for item in self.interactions_repository.all() if item.client_id == record_id])}",
            ],
        }
