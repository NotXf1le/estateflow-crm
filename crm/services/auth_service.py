from __future__ import annotations

import hashlib
import hmac
import logging
import os

from crm.config import DEFAULT_ADMIN_PASSWORD, DEFAULT_ADMIN_USERNAME, PBKDF2_ITERATIONS
from crm.enums import AuditAction, Role
from crm.models import User
from crm.repositories.users_repository import UsersRepository
from crm.services.audit_service import AuditService
from crm.utils import generate_entity_id, now_iso
from crm.validators import ValidationError, validate_user_payload


LOGGER = logging.getLogger(__name__)


class AuthService:
    def __init__(self, users_repository: UsersRepository, audit_service: AuditService) -> None:
        self.users_repository = users_repository
        self.audit_service = audit_service

    def hash_password(self, password: str, salt: bytes | None = None) -> str:
        salt = salt or os.urandom(16)
        digest = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            PBKDF2_ITERATIONS,
        )
        return f"{salt.hex()}${digest.hex()}"

    def verify_password(self, password: str, password_hash: str) -> bool:
        try:
            salt_hex, digest_hex = password_hash.split("$", 1)
        except ValueError:
            return False
        expected = self.hash_password(password, bytes.fromhex(salt_hex)).split("$", 1)[1]
        return hmac.compare_digest(expected, digest_hex)

    def ensure_default_admin(self) -> User:
        users = self.users_repository.all()
        if users:
            return users[0]
        timestamp = now_iso()
        admin = User(
            user_id=generate_entity_id("USR"),
            username=DEFAULT_ADMIN_USERNAME,
            full_name="System Administrator",
            role=Role.ADMIN.value,
            phone="+38267000000",
            email="admin@estateflow.local",
            password_hash=self.hash_password(DEFAULT_ADMIN_PASSWORD),
            is_active="1",
            created_at=timestamp,
            updated_at=timestamp,
        )
        created = self.users_repository.create(admin)
        LOGGER.info("Created default admin account.")
        self.audit_service.log(
            actor_user_id=created.user_id,
            entity_type="user",
            entity_id=created.user_id,
            action=AuditAction.CREATE,
            details="Default admin account created",
        )
        return created

    def login(self, username: str, password: str) -> dict[str, str]:
        user = self.users_repository.get_by_username(username)
        if not user or user.is_active != "1" or not self.verify_password(password, user.password_hash):
            self.audit_service.log(
                actor_user_id="",
                entity_type="user",
                entity_id=username.strip().lower(),
                action=AuditAction.LOGIN_FAILURE,
                details="Login failed",
            )
            raise ValidationError("Invalid username or password.")
        self.audit_service.log(
            actor_user_id=user.user_id,
            entity_type="user",
            entity_id=user.user_id,
            action=AuditAction.LOGIN_SUCCESS,
            details="Login successful",
        )
        return user.to_dict()

    def validate_user(self, payload: dict[str, str], *, existing_user_id: str | None = None) -> dict[str, str]:
        normalized = validate_user_payload(payload)
        existing = self.users_repository.get_by_username(normalized["username"])
        if existing and existing.user_id != existing_user_id:
            raise ValidationError("Username must be unique.")
        password = payload.get("password", "").strip()
        if existing_user_id is None and not password:
            raise ValidationError("Password is required.")
        if password:
            normalized["password_hash"] = self.hash_password(password)
        elif existing_user_id:
            current = self.users_repository.get(existing_user_id)
            normalized["password_hash"] = current.password_hash if current else ""
        return normalized
