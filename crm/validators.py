from __future__ import annotations

import re
from datetime import date, datetime
from decimal import Decimal
from typing import Iterable

from crm.config import DEFAULT_CURRENCY
from crm.enums import (
    AppointmentStatus,
    ClientRoleType,
    ClientStatus,
    DealStage,
    DealStatus,
    DealType,
    InteractionType,
    ListingType,
    PropertyStatus,
    PropertyType,
    RelatedEntityType,
    Role,
    TaskPriority,
    TaskStatus,
)
from crm.utils import clean_text, decimal_to_str, parse_decimal


EMAIL_PATTERN = re.compile(r"^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$", re.IGNORECASE)
PHONE_PATTERN = re.compile(r"^[0-9+\-/() ]{6,20}$")


class ValidationError(ValueError):
    """Raised when a record fails domain validation."""


def normalized_optional(value: str) -> str:
    return clean_text(value)


def required_text(value: str, field_label: str) -> str:
    cleaned = clean_text(value)
    if not cleaned:
        raise ValidationError(f"{field_label} is required.")
    return cleaned


def choice(value: str, field_label: str, options: Iterable[str]) -> str:
    cleaned = required_text(value, field_label).lower()
    normalized_options = {str(option).lower() for option in options}
    if cleaned not in normalized_options:
        raise ValidationError(f"{field_label} has an invalid value.")
    return cleaned


def optional_email(value: str) -> str:
    cleaned = clean_text(value).lower()
    if cleaned and not EMAIL_PATTERN.match(cleaned):
        raise ValidationError("Email format is invalid.")
    return cleaned


def optional_phone(value: str) -> str:
    cleaned = clean_text(value)
    if cleaned and not PHONE_PATTERN.match(cleaned):
        raise ValidationError("Phone number format is invalid.")
    return cleaned


def optional_decimal(value: str, field_label: str, minimum: Decimal | None = None) -> str:
    cleaned = clean_text(value)
    if not cleaned:
        return ""
    parsed = parse_decimal(cleaned)
    if parsed is None:
        raise ValidationError(f"{field_label} must be a valid number.")
    if minimum is not None and parsed < minimum:
        raise ValidationError(f"{field_label} must be at least {minimum}.")
    return decimal_to_str(parsed)


def optional_int(value: str, field_label: str, minimum: int | None = None) -> str:
    cleaned = clean_text(value)
    if not cleaned:
        return ""
    if not re.fullmatch(r"-?\d+", cleaned):
        raise ValidationError(f"{field_label} must be a whole number.")
    parsed = int(cleaned)
    if minimum is not None and parsed < minimum:
        raise ValidationError(f"{field_label} must be at least {minimum}.")
    return str(parsed)


def iso_date(value: str, field_label: str, required: bool = False) -> str:
    cleaned = clean_text(value)
    if not cleaned and not required:
        return ""
    if not cleaned and required:
        raise ValidationError(f"{field_label} is required.")
    try:
        date.fromisoformat(cleaned)
    except ValueError as error:
        raise ValidationError(f"{field_label} must be in YYYY-MM-DD format.") from error
    return cleaned


def iso_time(value: str, field_label: str, required: bool = False) -> str:
    cleaned = clean_text(value)
    if not cleaned and not required:
        return ""
    if not cleaned and required:
        raise ValidationError(f"{field_label} is required.")
    try:
        datetime.strptime(cleaned, "%H:%M")
    except ValueError as error:
        raise ValidationError(f"{field_label} must be in HH:MM format.") from error
    return cleaned


def iso_datetime(value: str, field_label: str, required: bool = False) -> str:
    cleaned = clean_text(value)
    if not cleaned and not required:
        return ""
    if not cleaned and required:
        raise ValidationError(f"{field_label} is required.")
    try:
        datetime.fromisoformat(cleaned)
    except ValueError as error:
        raise ValidationError(f"{field_label} must be a valid ISO datetime.") from error
    return cleaned


def validate_user_payload(payload: dict[str, str]) -> dict[str, str]:
    normalized = dict(payload)
    normalized["username"] = required_text(payload.get("username", ""), "Username").lower()
    normalized["full_name"] = required_text(payload.get("full_name", ""), "Full name")
    normalized["role"] = choice(payload.get("role", ""), "Role", [role.value for role in Role])
    normalized["phone"] = optional_phone(payload.get("phone", ""))
    normalized["email"] = optional_email(payload.get("email", ""))
    normalized["is_active"] = "1" if str(payload.get("is_active", "1")).strip() in {"1", "true", "True", "yes"} else "0"
    return normalized


def validate_client_payload(payload: dict[str, str]) -> dict[str, str]:
    normalized = dict(payload)
    normalized["full_name"] = required_text(payload.get("full_name", ""), "Full name")
    normalized["phone"] = optional_phone(payload.get("phone", ""))
    normalized["email"] = optional_email(payload.get("email", ""))
    normalized["role_type"] = choice(payload.get("role_type", ""), "Client role", [item.value for item in ClientRoleType])
    normalized["status"] = choice(payload.get("status", ""), "Status", [item.value for item in ClientStatus])
    normalized["assigned_agent_id"] = normalized_optional(payload.get("assigned_agent_id", ""))
    normalized["budget_min"] = optional_decimal(payload.get("budget_min", ""), "Minimum budget", Decimal("0"))
    normalized["budget_max"] = optional_decimal(payload.get("budget_max", ""), "Maximum budget", Decimal("0"))
    normalized["preferred_city"] = normalized_optional(payload.get("preferred_city", ""))
    normalized["preferred_property_type"] = normalized_optional(payload.get("preferred_property_type", ""))
    normalized["notes"] = normalized_optional(payload.get("notes", ""))
    if normalized["budget_min"] and normalized["budget_max"]:
        if Decimal(normalized["budget_min"]) > Decimal(normalized["budget_max"]):
            raise ValidationError("Minimum budget cannot be higher than maximum budget.")
    return normalized


def validate_property_payload(payload: dict[str, str]) -> dict[str, str]:
    normalized = dict(payload)
    normalized["title"] = required_text(payload.get("title", ""), "Listing title")
    normalized["listing_type"] = choice(payload.get("listing_type", ""), "Listing type", [item.value for item in ListingType])
    normalized["property_type"] = choice(payload.get("property_type", ""), "Property type", [item.value for item in PropertyType])
    normalized["address"] = required_text(payload.get("address", ""), "Address")
    normalized["city"] = required_text(payload.get("city", ""), "City")
    normalized["area_sqm"] = optional_decimal(payload.get("area_sqm", ""), "Area", Decimal("0"))
    normalized["rooms"] = optional_int(payload.get("rooms", ""), "Rooms", 0)
    normalized["bathrooms"] = optional_int(payload.get("bathrooms", ""), "Bathrooms", 0)
    normalized["floor"] = optional_int(payload.get("floor", ""), "Floor")
    normalized["price"] = optional_decimal(payload.get("price", ""), "Price", Decimal("0"))
    normalized["currency"] = clean_text(payload.get("currency", "")) or DEFAULT_CURRENCY
    normalized["owner_client_id"] = normalized_optional(payload.get("owner_client_id", ""))
    normalized["assigned_agent_id"] = normalized_optional(payload.get("assigned_agent_id", ""))
    normalized["status"] = choice(payload.get("status", ""), "Property status", [item.value for item in PropertyStatus])
    normalized["commission_rate"] = optional_decimal(payload.get("commission_rate", ""), "Commission rate", Decimal("0"))
    normalized["description"] = normalized_optional(payload.get("description", ""))
    return normalized


def validate_deal_payload(payload: dict[str, str]) -> dict[str, str]:
    normalized = dict(payload)
    normalized["client_id"] = required_text(payload.get("client_id", ""), "Client")
    normalized["property_id"] = required_text(payload.get("property_id", ""), "Property")
    normalized["agent_id"] = required_text(payload.get("agent_id", ""), "Agent")
    normalized["deal_type"] = choice(payload.get("deal_type", ""), "Deal type", [item.value for item in DealType])
    normalized["stage"] = choice(payload.get("stage", ""), "Deal stage", [item.value for item in DealStage])
    normalized["status"] = choice(payload.get("status", ""), "Deal status", [item.value for item in DealStatus])
    normalized["asking_price"] = optional_decimal(payload.get("asking_price", ""), "Asking price", Decimal("0"))
    normalized["offer_price"] = optional_decimal(payload.get("offer_price", ""), "Offer price", Decimal("0"))
    normalized["agreed_price"] = optional_decimal(payload.get("agreed_price", ""), "Agreed price", Decimal("0"))
    normalized["commission_rate"] = optional_decimal(payload.get("commission_rate", ""), "Commission rate", Decimal("0"))
    normalized["commission_amount"] = optional_decimal(payload.get("commission_amount", ""), "Commission amount", Decimal("0"))
    normalized["expected_close_date"] = iso_date(payload.get("expected_close_date", ""), "Expected close date")
    normalized["closed_date"] = iso_date(payload.get("closed_date", ""), "Closed date")
    normalized["notes"] = normalized_optional(payload.get("notes", ""))
    return normalized


def validate_appointment_payload(payload: dict[str, str]) -> dict[str, str]:
    normalized = dict(payload)
    normalized["title"] = required_text(payload.get("title", ""), "Appointment title")
    normalized["client_id"] = required_text(payload.get("client_id", ""), "Client")
    normalized["property_id"] = normalized_optional(payload.get("property_id", ""))
    normalized["agent_id"] = required_text(payload.get("agent_id", ""), "Agent")
    normalized["appointment_date"] = iso_date(payload.get("appointment_date", ""), "Appointment date", required=True)
    normalized["appointment_time"] = iso_time(payload.get("appointment_time", ""), "Appointment time", required=True)
    normalized["location"] = required_text(payload.get("location", ""), "Location")
    normalized["status"] = choice(payload.get("status", ""), "Appointment status", [item.value for item in AppointmentStatus])
    normalized["notes"] = normalized_optional(payload.get("notes", ""))
    return normalized


def validate_task_payload(payload: dict[str, str]) -> dict[str, str]:
    normalized = dict(payload)
    normalized["title"] = required_text(payload.get("title", ""), "Task title")
    normalized["related_entity_type"] = choice(
        payload.get("related_entity_type", ""),
        "Related entity type",
        [item.value for item in RelatedEntityType],
    )
    normalized["related_entity_id"] = normalized_optional(payload.get("related_entity_id", ""))
    normalized["assigned_agent_id"] = required_text(payload.get("assigned_agent_id", ""), "Assigned agent")
    normalized["due_date"] = iso_date(payload.get("due_date", ""), "Due date", required=True)
    normalized["priority"] = choice(payload.get("priority", ""), "Priority", [item.value for item in TaskPriority])
    normalized["status"] = choice(payload.get("status", ""), "Task status", [item.value for item in TaskStatus])
    normalized["notes"] = normalized_optional(payload.get("notes", ""))
    return normalized


def validate_interaction_payload(payload: dict[str, str]) -> dict[str, str]:
    normalized = dict(payload)
    normalized["interaction_type"] = choice(
        payload.get("interaction_type", ""),
        "Interaction type",
        [item.value for item in InteractionType],
    )
    normalized["client_id"] = normalized_optional(payload.get("client_id", ""))
    normalized["property_id"] = normalized_optional(payload.get("property_id", ""))
    normalized["deal_id"] = normalized_optional(payload.get("deal_id", ""))
    normalized["agent_id"] = required_text(payload.get("agent_id", ""), "Agent")
    normalized["interaction_datetime"] = iso_datetime(
        payload.get("interaction_datetime", ""),
        "Interaction datetime",
        required=True,
    )
    normalized["subject"] = required_text(payload.get("subject", ""), "Subject")
    normalized["summary"] = required_text(payload.get("summary", ""), "Summary")
    normalized["next_step"] = normalized_optional(payload.get("next_step", ""))
    if not (normalized["client_id"] or normalized["property_id"] or normalized["deal_id"]):
        raise ValidationError("An interaction must be linked to at least one client, property, or deal.")
    return normalized
