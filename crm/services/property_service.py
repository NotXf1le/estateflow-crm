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
from crm.validators import ValidationError, validate_property_payload


class PropertyService(BaseEntityService):
    entity_label = "Property"
    entity_type = "property"
    id_prefix = "PRP"
    search_fields = ("title", "address", "city", "description", "price")
    sort_field = "title"

    def __init__(
        self,
        repository: PropertiesRepository,
        audit_service: AuditService,
        *,
        users_repository: UsersRepository,
        clients_repository: ClientsRepository,
        deals_repository: DealsRepository,
        appointments_repository: AppointmentsRepository,
        tasks_repository: TasksRepository,
        interactions_repository: InteractionsRepository,
    ) -> None:
        super().__init__(repository, audit_service)
        self.users_repository = users_repository
        self.clients_repository = clients_repository
        self.deals_repository = deals_repository
        self.appointments_repository = appointments_repository
        self.tasks_repository = tasks_repository
        self.interactions_repository = interactions_repository

    def validate_payload(self, payload: dict[str, str], *, record_id: str | None = None) -> dict[str, str]:
        normalized = validate_property_payload(payload)
        owner_id = normalized.get("owner_client_id", "")
        if owner_id and not self.clients_repository.exists(owner_id):
            raise ValidationError("Owner client does not exist.")
        agent_id = normalized.get("assigned_agent_id", "")
        if agent_id and not self.users_repository.exists(agent_id):
            raise ValidationError("Assigned agent does not exist.")
        return normalized

    def dependency_error(self, record_id: str) -> str | None:
        referenced = []
        if any(item.property_id == record_id for item in self.deals_repository.all()):
            referenced.append("deals")
        if any(item.property_id == record_id for item in self.appointments_repository.all()):
            referenced.append("appointments")
        if any(item.property_id == record_id for item in self.interactions_repository.all()):
            referenced.append("interactions")
        if any(item.related_entity_type == "property" and item.related_entity_id == record_id for item in self.tasks_repository.all()):
            referenced.append("tasks")
        if referenced:
            return f"Property cannot be deleted because it is still referenced by: {', '.join(sorted(set(referenced)))}."
        return None

    def detail_sections(self, record_id: str) -> dict[str, list[str]]:
        property_row = self.repository.get(record_id)
        if not property_row:
            return {}
        owner = self.clients_repository.get(property_row.owner_client_id) if property_row.owner_client_id else None
        agent = self.users_repository.get(property_row.assigned_agent_id) if property_row.assigned_agent_id else None
        return {
            "Overview": [
                f"Type: {property_row.property_type}",
                f"Listing: {property_row.listing_type}",
                f"Status: {property_row.status}",
                f"Owner: {owner.full_name if owner else '-'}",
                f"Agent: {agent.full_name if agent else '-'}",
            ],
            "Activity": [
                f"Deals: {len([item for item in self.deals_repository.all() if item.property_id == record_id])}",
                f"Appointments: {len([item for item in self.appointments_repository.all() if item.property_id == record_id])}",
                f"Interactions: {len([item for item in self.interactions_repository.all() if item.property_id == record_id])}",
            ],
        }
