from __future__ import annotations

from decimal import Decimal

from crm.enums import DealStage, DealStatus
from crm.repositories.clients_repository import ClientsRepository
from crm.repositories.deals_repository import DealsRepository
from crm.repositories.interactions_repository import InteractionsRepository
from crm.repositories.properties_repository import PropertiesRepository
from crm.repositories.tasks_repository import TasksRepository
from crm.repositories.users_repository import UsersRepository
from crm.services.audit_service import AuditService
from crm.services.base_service import BaseEntityService
from crm.utils import decimal_to_str
from crm.validators import ValidationError, validate_deal_payload


class DealService(BaseEntityService):
    entity_label = "Deal"
    entity_type = "deal"
    id_prefix = "DEA"
    search_fields = ("deal_id", "client_id", "property_id", "notes", "stage", "status")
    sort_field = "updated_at"

    def __init__(
        self,
        repository: DealsRepository,
        audit_service: AuditService,
        *,
        users_repository: UsersRepository,
        clients_repository: ClientsRepository,
        properties_repository: PropertiesRepository,
        tasks_repository: TasksRepository,
        interactions_repository: InteractionsRepository,
    ) -> None:
        super().__init__(repository, audit_service)
        self.users_repository = users_repository
        self.clients_repository = clients_repository
        self.properties_repository = properties_repository
        self.tasks_repository = tasks_repository
        self.interactions_repository = interactions_repository

    def validate_payload(self, payload: dict[str, str], *, record_id: str | None = None) -> dict[str, str]:
        normalized = validate_deal_payload(payload)
        if not self.clients_repository.exists(normalized["client_id"]):
            raise ValidationError("Client does not exist.")
        if not self.properties_repository.exists(normalized["property_id"]):
            raise ValidationError("Property does not exist.")
        if not self.users_repository.exists(normalized["agent_id"]):
            raise ValidationError("Agent does not exist.")
        stage = normalized["stage"]
        status = normalized["status"]
        if stage == DealStage.CLOSED_WON.value:
            normalized["status"] = DealStatus.WON.value
        elif stage == DealStage.CLOSED_LOST.value:
            normalized["status"] = DealStatus.LOST.value
        elif status == DealStatus.WON.value:
            normalized["stage"] = DealStage.CLOSED_WON.value
        elif status == DealStatus.LOST.value:
            normalized["stage"] = DealStage.CLOSED_LOST.value
        agreed_price = Decimal(normalized["agreed_price"] or "0")
        commission_rate = Decimal(normalized["commission_rate"] or "0")
        if not normalized["commission_amount"] and agreed_price and commission_rate:
            normalized["commission_amount"] = decimal_to_str(agreed_price * commission_rate / Decimal("100"))
        if normalized["status"] in {DealStatus.WON.value, DealStatus.LOST.value} and not normalized["closed_date"]:
            from crm.utils import today_iso

            normalized["closed_date"] = today_iso()
        return normalized

    def dependency_error(self, record_id: str) -> str | None:
        referenced = []
        if any(item.deal_id == record_id for item in self.interactions_repository.all()):
            referenced.append("interactions")
        if any(item.related_entity_type == "deal" and item.related_entity_id == record_id for item in self.tasks_repository.all()):
            referenced.append("tasks")
        if referenced:
            return f"Deal cannot be deleted because it is still referenced by: {', '.join(sorted(set(referenced)))}."
        return None

    def detail_sections(self, record_id: str) -> dict[str, list[str]]:
        deal = self.repository.get(record_id)
        if not deal:
            return {}
        client = self.clients_repository.get(deal.client_id)
        property_row = self.properties_repository.get(deal.property_id)
        agent = self.users_repository.get(deal.agent_id)
        return {
            "Pipeline": [
                f"Client: {client.full_name if client else deal.client_id}",
                f"Property: {property_row.title if property_row else deal.property_id}",
                f"Agent: {agent.full_name if agent else deal.agent_id}",
                f"Stage: {deal.stage}",
                f"Status: {deal.status}",
                f"Commission: {deal.commission_amount or '-'} EUR",
            ],
            "Follow-up": [
                f"Tasks linked: {len([item for item in self.tasks_repository.all() if item.related_entity_type == 'deal' and item.related_entity_id == record_id])}",
                f"Interactions linked: {len([item for item in self.interactions_repository.all() if item.deal_id == record_id])}",
            ],
        }
