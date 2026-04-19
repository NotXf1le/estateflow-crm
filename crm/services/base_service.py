from __future__ import annotations

import csv
from pathlib import Path

from crm.enums import AuditAction
from crm.repositories.base_csv_repository import BaseCSVRepository
from crm.services.audit_service import AuditService
from crm.utils import generate_entity_id, now_iso, query_records
from crm.validators import ValidationError


class BaseEntityService:
    """Base CRUD and import/export logic for CSV-backed entities."""

    entity_label = "Record"
    entity_type = "record"
    id_prefix = "REC"
    search_fields: tuple[str, ...] = ()
    sort_field = ""

    def __init__(self, repository: BaseCSVRepository, audit_service: AuditService) -> None:
        self.repository = repository
        self.audit_service = audit_service

    @property
    def id_field(self) -> str:
        return self.repository.id_field

    def list_records(
        self,
        *,
        search_text: str = "",
        filters: dict[str, str] | None = None,
        sort_field: str | None = None,
        reverse: bool = False,
    ) -> list[dict[str, str]]:
        return query_records(
            self.repository.all_dicts(),
            search_text=search_text,
            search_fields=self.search_fields,
            filters=filters,
            sort_field=sort_field or self.sort_field,
            reverse=reverse,
        )

    def get_record(self, record_id: str) -> dict[str, str] | None:
        record = self.repository.get(record_id)
        return record.to_dict() if record else None

    def validate_payload(self, payload: dict[str, str], *, record_id: str | None = None) -> dict[str, str]:
        return payload

    def build_model(self, payload: dict[str, str]):
        return self.repository.model_cls.from_dict(payload)

    def enrich_before_save(self, payload: dict[str, str], *, is_new: bool) -> dict[str, str]:
        return payload

    def dependency_error(self, record_id: str) -> str | None:
        return None

    def detail_sections(self, record_id: str) -> dict[str, list[str]]:
        return {}

    def create_record(self, payload: dict[str, str], actor_user_id: str = "") -> dict[str, str]:
        normalized = self.validate_payload(payload, record_id=None)
        timestamp = now_iso()
        normalized[self.id_field] = generate_entity_id(self.id_prefix)
        if "created_at" in self.repository.headers:
            normalized["created_at"] = timestamp
        if "updated_at" in self.repository.headers:
            normalized["updated_at"] = timestamp
        normalized = self.enrich_before_save(normalized, is_new=True)
        created = self.repository.create(self.build_model(normalized))
        self.audit_service.log(
            actor_user_id=actor_user_id,
            entity_type=self.entity_type,
            entity_id=getattr(created, self.id_field),
            action=AuditAction.CREATE,
            details=f"{self.entity_label} created",
        )
        return created.to_dict()

    def update_record(self, record_id: str, payload: dict[str, str], actor_user_id: str = "") -> dict[str, str]:
        existing = self.repository.get(record_id)
        if not existing:
            raise ValidationError(f"{self.entity_label} was not found.")
        normalized = self.validate_payload(payload, record_id=record_id)
        normalized[self.id_field] = record_id
        if "created_at" in self.repository.headers:
            normalized["created_at"] = getattr(existing, "created_at", "")
        if "updated_at" in self.repository.headers:
            normalized["updated_at"] = now_iso()
        normalized = self.enrich_before_save(normalized, is_new=False)
        updated = self.repository.update(record_id, self.build_model(normalized))
        self.audit_service.log(
            actor_user_id=actor_user_id,
            entity_type=self.entity_type,
            entity_id=record_id,
            action=AuditAction.UPDATE,
            details=f"{self.entity_label} updated",
        )
        return updated.to_dict()

    def delete_record(self, record_id: str, actor_user_id: str = "") -> bool:
        error_message = self.dependency_error(record_id)
        if error_message:
            raise ValidationError(error_message)
        deleted = self.repository.delete(record_id)
        if deleted:
            self.audit_service.log(
                actor_user_id=actor_user_id,
                entity_type=self.entity_type,
                entity_id=record_id,
                action=AuditAction.DELETE,
                details=f"{self.entity_label} deleted",
            )
        return deleted

    def export_records(self, target_path: Path, rows: list[dict[str, str]], actor_user_id: str = "") -> Path:
        target_path.parent.mkdir(parents=True, exist_ok=True)
        with target_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(self.repository.headers))
            writer.writeheader()
            writer.writerows(rows)
        self.audit_service.log(
            actor_user_id=actor_user_id,
            entity_type=self.entity_type,
            entity_id="*",
            action=AuditAction.EXPORT,
            details=f"Exported {len(rows)} records to {target_path.name}",
        )
        return target_path

    def import_records(self, source_path: Path, actor_user_id: str = "") -> tuple[int, int]:
        created_count = 0
        updated_count = 0
        with source_path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                payload = {field: str(row.get(field, "") or "").strip() for field in self.repository.headers}
                record_id = payload.get(self.id_field, "")
                if record_id and self.repository.exists(record_id):
                    self.update_record(record_id, payload, actor_user_id=actor_user_id)
                    updated_count += 1
                else:
                    payload[self.id_field] = ""
                    self.create_record(payload, actor_user_id=actor_user_id)
                    created_count += 1
        self.audit_service.log(
            actor_user_id=actor_user_id,
            entity_type=self.entity_type,
            entity_id="*",
            action=AuditAction.IMPORT,
            details=f"Imported {created_count} new and {updated_count} updated records from {source_path.name}",
        )
        return created_count, updated_count
