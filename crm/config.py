from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


APP_NAME = "EstateFlow CRM"
APP_VERSION = "1.0.0"
DEFAULT_CURRENCY = "EUR"
DEFAULT_APPEARANCE_MODE = "Dark"
DEFAULT_COLOR_THEME = "blue"
DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "Admin123!"
PBKDF2_ITERATIONS = 120_000
APP_LOG_FILE = "logs/app.log"

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
LOG_DIR = BASE_DIR / "logs"
EXPORT_DIR = BASE_DIR / "exports"
BACKUP_DIR = BASE_DIR / "backups"


@dataclass(frozen=True)
class CsvDefinition:
    name: str
    file_name: str
    headers: tuple[str, ...]

    @property
    def path(self) -> Path:
        return DATA_DIR / self.file_name


CSV_DEFINITIONS: dict[str, CsvDefinition] = {
    "users": CsvDefinition(
        name="users",
        file_name="users.csv",
        headers=(
            "user_id",
            "username",
            "full_name",
            "role",
            "phone",
            "email",
            "password_hash",
            "is_active",
            "created_at",
            "updated_at",
        ),
    ),
    "clients": CsvDefinition(
        name="clients",
        file_name="clients.csv",
        headers=(
            "client_id",
            "full_name",
            "phone",
            "email",
            "role_type",
            "status",
            "assigned_agent_id",
            "budget_min",
            "budget_max",
            "preferred_city",
            "preferred_property_type",
            "notes",
            "created_at",
            "updated_at",
        ),
    ),
    "properties": CsvDefinition(
        name="properties",
        file_name="properties.csv",
        headers=(
            "property_id",
            "title",
            "listing_type",
            "property_type",
            "address",
            "city",
            "area_sqm",
            "rooms",
            "bathrooms",
            "floor",
            "price",
            "currency",
            "owner_client_id",
            "assigned_agent_id",
            "status",
            "commission_rate",
            "description",
            "created_at",
            "updated_at",
        ),
    ),
    "deals": CsvDefinition(
        name="deals",
        file_name="deals.csv",
        headers=(
            "deal_id",
            "client_id",
            "property_id",
            "agent_id",
            "deal_type",
            "stage",
            "status",
            "asking_price",
            "offer_price",
            "agreed_price",
            "commission_rate",
            "commission_amount",
            "expected_close_date",
            "closed_date",
            "notes",
            "created_at",
            "updated_at",
        ),
    ),
    "appointments": CsvDefinition(
        name="appointments",
        file_name="appointments.csv",
        headers=(
            "appointment_id",
            "title",
            "client_id",
            "property_id",
            "agent_id",
            "appointment_date",
            "appointment_time",
            "location",
            "status",
            "notes",
            "created_at",
            "updated_at",
        ),
    ),
    "tasks": CsvDefinition(
        name="tasks",
        file_name="tasks.csv",
        headers=(
            "task_id",
            "title",
            "related_entity_type",
            "related_entity_id",
            "assigned_agent_id",
            "due_date",
            "priority",
            "status",
            "notes",
            "created_at",
            "updated_at",
        ),
    ),
    "interactions": CsvDefinition(
        name="interactions",
        file_name="interactions.csv",
        headers=(
            "interaction_id",
            "interaction_type",
            "client_id",
            "property_id",
            "deal_id",
            "agent_id",
            "interaction_datetime",
            "subject",
            "summary",
            "next_step",
            "created_at",
        ),
    ),
    "audit_log": CsvDefinition(
        name="audit_log",
        file_name="audit_log.csv",
        headers=(
            "audit_id",
            "actor_user_id",
            "entity_type",
            "entity_id",
            "action",
            "details",
            "created_at",
        ),
    ),
}


def ensure_directories() -> None:
    for directory in (DATA_DIR, LOG_DIR, EXPORT_DIR, BACKUP_DIR):
        directory.mkdir(parents=True, exist_ok=True)


def schema_headers(name: str) -> tuple[str, ...]:
    return CSV_DEFINITIONS[name].headers


def as_choices(values: Any) -> list[str]:
    return [str(item.value if hasattr(item, "value") else item) for item in values]
