from __future__ import annotations

import csv
import logging
import os
import re
import shutil
import tempfile
from datetime import date, datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path
from typing import Iterable, Sequence
from uuid import uuid4

from crm.config import BACKUP_DIR


LOGGER = logging.getLogger(__name__)


def now_iso() -> str:
    return datetime.now().replace(microsecond=0).isoformat()


def today_iso() -> str:
    return date.today().isoformat()


def format_iso_for_ui(value: str) -> str:
    if not value:
        return ""
    try:
        return datetime.fromisoformat(value).strftime("%d.%m.%Y %H:%M")
    except ValueError:
        try:
            return datetime.strptime(value, "%Y-%m-%d").strftime("%d.%m.%Y")
        except ValueError:
            return value


def generate_entity_id(prefix: str) -> str:
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    suffix = uuid4().hex[:6].upper()
    return f"{prefix}-{timestamp}-{suffix}"


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def ensure_csv_file(path: Path, headers: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        return
    write_csv_rows(path, headers, [])


def read_csv_rows(path: Path, headers: Sequence[str]) -> list[dict[str, str]]:
    ensure_csv_file(path, headers)
    with path.open("r", encoding="utf-8", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        rows: list[dict[str, str]] = []
        for row in reader:
            normalized_row = {header: str(row.get(header, "") or "").strip() for header in headers}
            if not any(normalized_row.values()):
                continue
            rows.append(normalized_row)
        return rows


def write_csv_rows(path: Path, headers: Sequence[str], rows: Iterable[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        newline="",
        delete=False,
        dir=path.parent,
        suffix=".tmp",
    ) as temp_file:
        writer = csv.DictWriter(temp_file, fieldnames=list(headers))
        writer.writeheader()
        for row in rows:
            normalized = {header: str(row.get(header, "") or "").strip() for header in headers}
            writer.writerow(normalized)
        temp_name = temp_file.name
    os.replace(temp_name, path)


def decimal_to_str(value: Decimal | None) -> str:
    if value is None:
        return ""
    normalized = value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return format(normalized, "f")


def parse_decimal(value: str, default: Decimal | None = None) -> Decimal | None:
    cleaned = clean_text(value)
    if not cleaned:
        return default
    cleaned = cleaned.replace(",", ".")
    try:
        return Decimal(cleaned)
    except (InvalidOperation, ValueError):
        return default


def ensure_backup_snapshot(data_dir: Path) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    target_dir = BACKUP_DIR / f"snapshot-{timestamp}"
    target_dir.mkdir(parents=True, exist_ok=True)
    for file_path in data_dir.glob("*.csv"):
        shutil.copy2(file_path, target_dir / file_path.name)
    LOGGER.info("Created backup snapshot in %s", target_dir)
    return target_dir


def query_records(
    records: Sequence[dict[str, str]],
    *,
    search_text: str = "",
    search_fields: Sequence[str] | None = None,
    filters: dict[str, str] | None = None,
    sort_field: str | None = None,
    reverse: bool = False,
) -> list[dict[str, str]]:
    search_fields = list(search_fields or [])
    filters = {key: value for key, value in (filters or {}).items() if clean_text(value)}
    needle = clean_text(search_text).lower()
    filtered: list[dict[str, str]] = []
    for record in records:
        if filters and any(clean_text(record.get(field, "")).lower() != clean_text(value).lower() for field, value in filters.items()):
            continue
        if needle and search_fields:
            haystack = " ".join(clean_text(record.get(field, "")) for field in search_fields).lower()
            if needle not in haystack:
                continue
        filtered.append(dict(record))
    if sort_field:
        filtered.sort(key=lambda row: clean_text(row.get(sort_field, "")).lower(), reverse=reverse)
    return filtered
