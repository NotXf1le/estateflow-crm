from __future__ import annotations

from crm.models import Client
from crm.repositories.clients_repository import ClientsRepository
from tests.common import SandboxPathsTestCase


class RepositoryTests(SandboxPathsTestCase):
    def test_repository_initializes_missing_csv_with_header(self) -> None:
        repository = ClientsRepository()
        self.assertTrue(repository.path.exists())
        content = repository.path.read_text(encoding="utf-8").splitlines()
        self.assertEqual(content[0], ",".join(repository.headers))

    def test_create_read_update_delete_roundtrip(self) -> None:
        repository = ClientsRepository()
        client = Client(
            client_id="CLI-001",
            full_name="Marko Vukovic",
            phone="+38267111222",
            email="marko@example.com",
            role_type="buyer",
            status="active",
            assigned_agent_id="USR-001",
            budget_min="80000.00",
            budget_max="120000.00",
            preferred_city="Podgorica",
            preferred_property_type="apartment",
            notes="Interested in city center.",
            created_at="2026-04-19T10:00:00",
            updated_at="2026-04-19T10:00:00",
        )
        repository.create(client)
        loaded = repository.get("CLI-001")
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.full_name, "Marko Vukovic")

        client.notes = "Updated note"
        repository.update("CLI-001", client)
        updated = repository.get("CLI-001")
        self.assertEqual(updated.notes, "Updated note")

        deleted = repository.delete("CLI-001")
        self.assertTrue(deleted)
        self.assertIsNone(repository.get("CLI-001"))
