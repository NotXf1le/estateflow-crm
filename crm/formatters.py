from __future__ import annotations

from decimal import Decimal

from crm.utils import format_iso_for_ui, parse_decimal


def format_currency(value: str, currency: str = "EUR") -> str:
    parsed = parse_decimal(value, Decimal("0"))
    return f"{parsed:,.2f} {currency}".replace(",", " ")


def format_percent(value: str) -> str:
    parsed = parse_decimal(value, Decimal("0"))
    return f"{parsed:.2f}%"


def format_count(value: int) -> str:
    return f"{value:,}".replace(",", " ")


def format_datetime(value: str) -> str:
    return format_iso_for_ui(value)


def bool_to_label(value: str) -> str:
    return "Yes" if value == "1" else "No"
