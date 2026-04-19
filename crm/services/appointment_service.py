from __future__ import annotations

from datetime import datetime

from crm.repositories.appointments_repository import AppointmentsRepository
from crm.repositories.clients_repository import ClientsRepository
from crm.repositories.properties_repository import PropertiesRepository
from crm.repositories.users_repository import UsersRepository
from crm.services.audit_service import AuditService
from crm.services.base_service import BaseEntityService
from crm.validators import ValidationError, validate_appointment_payload


class AppointmentService(BaseEntityService):
    entity_label = "Appointment"
    entity_type = "appointment"
    id_prefix = "APP"
    search_fields = ("title", "location", "status", "notes")
    sort_field = "appointment_date"

    def __init__(
        self,
        repository: AppointmentsRepository,
        audit_service: AuditService,
        *,
        users_repository: UsersRepository,
        clients_repository: ClientsRepository,
        properties_repository: PropertiesRepository,
    ) -> None:
        super().__init__(repository, audit_service)
        self.users_repository = users_repository
        self.clients_repository = clients_repository
        self.properties_repository = properties_repository

    def validate_payload(self, payload: dict[str, str], *, record_id: str | None = None) -> dict[str, str]:
        normalized = validate_appointment_payload(payload)
        if not self.clients_repository.exists(normalized["client_id"]):
            raise ValidationError("Client does not exist.")
        if normalized["property_id"] and not self.properties_repository.exists(normalized["property_id"]):
            raise ValidationError("Property does not exist.")
        if not self.users_repository.exists(normalized["agent_id"]):
            raise ValidationError("Agent does not exist.")
        return normalized

    def is_overdue(self, record: dict[str, str]) -> bool:
        if record.get("status") != "scheduled":
            return False
        try:
            scheduled_for = datetime.fromisoformat(f"{record['appointment_date']}T{record['appointment_time']}")
        except (KeyError, ValueError):
            return False
        return scheduled_for < datetime.now()

    def upcoming(self, limit: int = 10) -> list[dict[str, str]]:
        rows = [
            row
            for row in self.repository.all_dicts()
            if row.get("status") == "scheduled" and not self.is_overdue(row)
        ]
        rows.sort(key=lambda item: (item.get("appointment_date", ""), item.get("appointment_time", "")))
        return rows[:limit]

    def detail_sections(self, record_id: str) -> dict[str, list[str]]:
        appointment = self.repository.get(record_id)
        if not appointment:
            return {}
        client = self.clients_repository.get(appointment.client_id)
        property_row = self.properties_repository.get(appointment.property_id) if appointment.property_id else None
        agent = self.users_repository.get(appointment.agent_id)
        overdue = "Yes" if self.is_overdue(appointment.to_dict()) else "No"
        return {
            "Schedule": [
                f"Client: {client.full_name if client else appointment.client_id}",
                f"Property: {property_row.title if property_row else '-'}",
                f"Agent: {agent.full_name if agent else appointment.agent_id}",
                f"Date: {appointment.appointment_date} {appointment.appointment_time}",
                f"Overdue: {overdue}",
            ]
        }
