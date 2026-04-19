from __future__ import annotations

from dataclasses import asdict, dataclass, fields
from typing import Any, ClassVar


@dataclass
class CSVModel:
    id_field: ClassVar[str]
    entity_name: ClassVar[str]

    def to_dict(self) -> dict[str, str]:
        return {
            field.name: str(getattr(self, field.name, "") or "")
            for field in fields(self)
        }

    @classmethod
    def from_dict(cls, row: dict[str, Any]) -> "CSVModel":
        values = {}
        for field in fields(cls):
            raw_value = row.get(field.name, "")
            values[field.name] = str(raw_value or "").strip()
        return cls(**values)

    def asdict(self) -> dict[str, str]:
        return asdict(self)


@dataclass
class User(CSVModel):
    id_field: ClassVar[str] = "user_id"
    entity_name: ClassVar[str] = "user"

    user_id: str = ""
    username: str = ""
    full_name: str = ""
    role: str = ""
    phone: str = ""
    email: str = ""
    password_hash: str = ""
    is_active: str = "1"
    created_at: str = ""
    updated_at: str = ""


@dataclass
class Client(CSVModel):
    id_field: ClassVar[str] = "client_id"
    entity_name: ClassVar[str] = "client"

    client_id: str = ""
    full_name: str = ""
    phone: str = ""
    email: str = ""
    role_type: str = ""
    status: str = ""
    assigned_agent_id: str = ""
    budget_min: str = ""
    budget_max: str = ""
    preferred_city: str = ""
    preferred_property_type: str = ""
    notes: str = ""
    created_at: str = ""
    updated_at: str = ""


@dataclass
class Property(CSVModel):
    id_field: ClassVar[str] = "property_id"
    entity_name: ClassVar[str] = "property"

    property_id: str = ""
    title: str = ""
    listing_type: str = ""
    property_type: str = ""
    address: str = ""
    city: str = ""
    area_sqm: str = ""
    rooms: str = ""
    bathrooms: str = ""
    floor: str = ""
    price: str = ""
    currency: str = "EUR"
    owner_client_id: str = ""
    assigned_agent_id: str = ""
    status: str = ""
    commission_rate: str = ""
    description: str = ""
    created_at: str = ""
    updated_at: str = ""


@dataclass
class Deal(CSVModel):
    id_field: ClassVar[str] = "deal_id"
    entity_name: ClassVar[str] = "deal"

    deal_id: str = ""
    client_id: str = ""
    property_id: str = ""
    agent_id: str = ""
    deal_type: str = ""
    stage: str = ""
    status: str = ""
    asking_price: str = ""
    offer_price: str = ""
    agreed_price: str = ""
    commission_rate: str = ""
    commission_amount: str = ""
    expected_close_date: str = ""
    closed_date: str = ""
    notes: str = ""
    created_at: str = ""
    updated_at: str = ""


@dataclass
class Appointment(CSVModel):
    id_field: ClassVar[str] = "appointment_id"
    entity_name: ClassVar[str] = "appointment"

    appointment_id: str = ""
    title: str = ""
    client_id: str = ""
    property_id: str = ""
    agent_id: str = ""
    appointment_date: str = ""
    appointment_time: str = ""
    location: str = ""
    status: str = ""
    notes: str = ""
    created_at: str = ""
    updated_at: str = ""


@dataclass
class Task(CSVModel):
    id_field: ClassVar[str] = "task_id"
    entity_name: ClassVar[str] = "task"

    task_id: str = ""
    title: str = ""
    related_entity_type: str = ""
    related_entity_id: str = ""
    assigned_agent_id: str = ""
    due_date: str = ""
    priority: str = ""
    status: str = ""
    notes: str = ""
    created_at: str = ""
    updated_at: str = ""


@dataclass
class Interaction(CSVModel):
    id_field: ClassVar[str] = "interaction_id"
    entity_name: ClassVar[str] = "interaction"

    interaction_id: str = ""
    interaction_type: str = ""
    client_id: str = ""
    property_id: str = ""
    deal_id: str = ""
    agent_id: str = ""
    interaction_datetime: str = ""
    subject: str = ""
    summary: str = ""
    next_step: str = ""
    created_at: str = ""


@dataclass
class AuditLog(CSVModel):
    id_field: ClassVar[str] = "audit_id"
    entity_name: ClassVar[str] = "audit_log"

    audit_id: str = ""
    actor_user_id: str = ""
    entity_type: str = ""
    entity_id: str = ""
    action: str = ""
    details: str = ""
    created_at: str = ""
