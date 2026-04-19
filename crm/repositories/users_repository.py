from __future__ import annotations

from crm.config import CSV_DEFINITIONS
from crm.models import User
from crm.repositories.base_csv_repository import BaseCSVRepository


class UsersRepository(BaseCSVRepository[User]):
    def __init__(self) -> None:
        super().__init__(CSV_DEFINITIONS["users"].path, User)

    def get_by_username(self, username: str) -> User | None:
        normalized = username.strip().lower()
        for user in self.all():
            if user.username.lower() == normalized:
                return user
        return None
