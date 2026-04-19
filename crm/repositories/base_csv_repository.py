from __future__ import annotations

from dataclasses import fields
from pathlib import Path
from typing import Generic, TypeVar

from crm.models import CSVModel
from crm.utils import ensure_csv_file, read_csv_rows, write_csv_rows


ModelT = TypeVar("ModelT", bound=CSVModel)


class BaseCSVRepository(Generic[ModelT]):
    """Generic repository backed by a single CSV file."""

    def __init__(self, path: Path, model_cls: type[ModelT]) -> None:
        self.path = path
        self.model_cls = model_cls
        self.headers = tuple(field.name for field in fields(model_cls))
        self.id_field = model_cls.id_field
        ensure_csv_file(self.path, self.headers)

    def all(self) -> list[ModelT]:
        return [self.model_cls.from_dict(row) for row in read_csv_rows(self.path, self.headers)]

    def all_dicts(self) -> list[dict[str, str]]:
        return [item.to_dict() for item in self.all()]

    def get(self, record_id: str) -> ModelT | None:
        for item in self.all():
            if getattr(item, self.id_field) == record_id:
                return item
        return None

    def exists(self, record_id: str) -> bool:
        return self.get(record_id) is not None

    def save_all(self, records: list[ModelT]) -> None:
        rows = [record.to_dict() for record in records]
        write_csv_rows(self.path, self.headers, rows)

    def create(self, record: ModelT) -> ModelT:
        records = self.all()
        if any(getattr(item, self.id_field) == getattr(record, self.id_field) for item in records):
            raise ValueError(f"{self.model_cls.entity_name} with the same identifier already exists.")
        records.append(record)
        self.save_all(records)
        return record

    def update(self, record_id: str, record: ModelT) -> ModelT:
        records = self.all()
        updated = False
        for index, existing in enumerate(records):
            if getattr(existing, self.id_field) == record_id:
                records[index] = record
                updated = True
                break
        if not updated:
            raise ValueError(f"{self.model_cls.entity_name} was not found.")
        self.save_all(records)
        return record

    def delete(self, record_id: str) -> bool:
        records = self.all()
        filtered = [item for item in records if getattr(item, self.id_field) != record_id]
        if len(filtered) == len(records):
            return False
        self.save_all(filtered)
        return True

    def find_by(self, field_name: str, value: str) -> list[ModelT]:
        return [item for item in self.all() if getattr(item, field_name, "") == value]
