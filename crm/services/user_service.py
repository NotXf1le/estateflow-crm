from __future__ import annotations

from crm.enums import Role
from crm.repositories.appointments_repository import AppointmentsRepository
from crm.repositories.clients_repository import ClientsRepository
from crm.repositories.deals_repository import DealsRepository
from crm.repositories.interactions_repository import InteractionsRepository
from crm.repositories.properties_repository import PropertiesRepository
from crm.repositories.tasks_repository import TasksRepository
from crm.repositories.users_repository import UsersRepository
from crm.services.auth_service import AuthService
from crm.services.base_service import BaseEntityService
from crm.services.audit_service import AuditService
from crm.validators import ValidationError


class UserService(BaseEntityService):
    entity_label = "User"
    entity_type = "user"
    id_prefix = "USR"
    search_fields = ("username", "full_name", "email", "phone", "role")
    sort_field = "full_name"

    def __init__(
        self,
        repository: UsersRepository,
        audit_service: AuditService,
        auth_service: AuthService,
        *,
        clients_repository: ClientsRepository,
        properties_repository: PropertiesRepository,
        deals_repository: DealsRepository,
        appointments_repository: AppointmentsRepository,
        tasks_repository: TasksRepository,
        interactions_repository: InteractionsRepository,
    ) -> None:
        super().__init__(repository, audit_service)
        self.auth_service = auth_service
        self.clients_repository = clients_repository
        self.properties_repository = properties_repository
        self.deals_repository = deals_repository
        self.appointments_repository = appointments_repository
        self.tasks_repository = tasks_repository
        self.interactions_repository = interactions_repository

    def validate_payload(self, payload: dict[str, str], *, record_id: str | None = None) -> dict[str, str]:
        return self.auth_service.validate_user(payload, existing_user_id=record_id)

    def dependency_error(self, record_id: str) -> str | None:
        referenced = []
        if any(item.assigned_agent_id == record_id for item in self.clients_repository.all()):
            referenced.append("clients")
        if any(item.assigned_agent_id == record_id for item in self.properties_repository.all()):
            referenced.append("properties")
        if any(item.agent_id == record_id for item in self.deals_repository.all()):
            referenced.append("deals")
        if any(item.agent_id == record_id for item in self.appointments_repository.all()):
            referenced.append("appointments")
        if any(item.assigned_agent_id == record_id for item in self.tasks_repository.all()):
            referenced.append("tasks")
        if any(item.agent_id == record_id for item in self.interactions_repository.all()):
            referenced.append("interactions")
        user = self.repository.get(record_id)
        if user and user.role == Role.ADMIN.value:
            active_admins = [item for item in self.repository.all() if item.role == Role.ADMIN.value and item.is_active == "1"]
            if len(active_admins) <= 1:
                referenced.append("system administration")
        if referenced:
            return f"User cannot be deleted because it is still referenced by: {', '.join(sorted(set(referenced)))}."
        return None

    def detail_sections(self, record_id: str) -> dict[str, list[str]]:
        user = self.repository.get(record_id)
        if not user:
            return {}
        return {
            "Profile": [
                f"Username: {user.username}",
                f"Role: {user.role}",
                f"Email: {user.email or '-'}",
                f"Phone: {user.phone or '-'}",
                f"Active: {'Yes' if user.is_active == '1' else 'No'}",
            ],
            "Workload": [
                f"Assigned clients: {len([item for item in self.clients_repository.all() if item.assigned_agent_id == record_id])}",
                f"Assigned listings: {len([item for item in self.properties_repository.all() if item.assigned_agent_id == record_id])}",
                f"Open tasks: {len([item for item in self.tasks_repository.all() if item.assigned_agent_id == record_id and item.status != 'done'])}",
            ],
        }
