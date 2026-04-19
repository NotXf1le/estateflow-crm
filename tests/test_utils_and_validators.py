from __future__ import annotations

from crm.utils import generate_entity_id, query_records
from crm.validators import ValidationError, validate_client_payload
from tests.common import SandboxPathsTestCase


class UtilityAndValidationTests(SandboxPathsTestCase):
    def test_id_generation_uses_prefix_and_is_unique(self) -> None:
        first = generate_entity_id("CLI")
        second = generate_entity_id("CLI")
        self.assertTrue(first.startswith("CLI-"))
        self.assertTrue(second.startswith("CLI-"))
        self.assertNotEqual(first, second)

    def test_query_records_supports_search_filter_and_sort(self) -> None:
        rows = [
            {"name": "Ana Petrovic", "city": "Budva", "status": "active"},
            {"name": "Nikola Savic", "city": "Podgorica", "status": "active"},
            {"name": "Ivana Markovic", "city": "Budva", "status": "inactive"},
        ]
        result = query_records(
            rows,
            search_text="ana",
            search_fields=["name"],
            filters={"status": "active"},
            sort_field="city",
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Ana Petrovic")

    def test_client_validation_rejects_invalid_email(self) -> None:
        with self.assertRaises(ValidationError):
            validate_client_payload(
                {
                    "full_name": "Test Client",
                    "phone": "+38267111222",
                    "email": "bad-email",
                    "role_type": "buyer",
                    "status": "active",
                }
            )
