from __future__ import annotations

from crm.repositories.clients_repository import ClientsRepository
from crm.repositories.deals_repository import DealsRepository
from crm.repositories.interactions_repository import InteractionsRepository
from crm.repositories.properties_repository import PropertiesRepository
from crm.repositories.users_repository import UsersRepository
from crm.services.audit_service import AuditService
from crm.services.base_service import BaseEntityService
from crm.validators import ValidationError, validate_interaction_payload


class InteractionService(BaseEntityService):
    entity_label = "Interaction"
    entity_type = "interaction"
    id_prefix = "INT"
    search_fields = ("subject", "summary", "next_step", "interaction_type")
    sort_field = "interaction_datetime"

    def __init__(
        self,
        repository: InteractionsRepository,
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

    def validate_payload(self, payload: dict[str, str], *, record_id: str | None = None) -> dict[str, str]:
        normalized = validate_interaction_payload(payload)
        if not self.users_repository.exists(normalized["agent_id"]):
            raise ValidationError("Agent does not exist.")
        if normalized["client_id"] and not self.clients_repository.exists(normalized["client_id"]):
            raise ValidationError("Linked client does not exist.")
        if normalized["property_id"] and not self.properties_repository.exists(normalized["property_id"]):
            raise ValidationError("Linked property does not exist.")
        if normalized["deal_id"] and not self.deals_repository.exists(normalized["deal_id"]):
            raise ValidationError("Linked deal does not exist.")
        return normalized

    def timeline(self, *, client_id: str = "", property_id: str = "", deal_id: str = "") -> list[dict[str, str]]:
        rows = self.repository.all_dicts()
        filtered = []
        for row in rows:
            if client_id and row.get("client_id") != client_id:
                continue
            if property_id and row.get("property_id") != property_id:
                continue
            if deal_id and row.get("deal_id") != deal_id:
                continue
            filtered.append(row)
        filtered.sort(key=lambda item: item.get("interaction_datetime", ""), reverse=True)
        return filtered

    def detail_sections(self, record_id: str) -> dict[str, list[str]]:
        interaction = self.repository.get(record_id)
        if not interaction:
            return {}
        agent = self.users_repository.get(interaction.agent_id)
        return {
            "Timeline": [
                f"Type: {interaction.interaction_type}",
                f"Agent: {agent.full_name if agent else interaction.agent_id}",
                f"When: {interaction.interaction_datetime}",
                f"Client: {interaction.client_id or '-'}",
                f"Property: {interaction.property_id or '-'}",
                f"Deal: {interaction.deal_id or '-'}",
            ]
        }
