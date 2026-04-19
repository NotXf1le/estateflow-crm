from __future__ import annotations

from crm.bootstrap import build_context
from crm.validators import ValidationError
from tests.common import SandboxPathsTestCase


class ServiceTests(SandboxPathsTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.context = build_context()

    def test_default_admin_is_created(self) -> None:
        users = self.context.user_service.list_records()
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0]["username"], "admin")

    def test_deal_commission_is_auto_calculated(self) -> None:
        agent = self.context.user_service.list_records()[0]
        client = self.context.client_service.create_record(
            {
                "full_name": "Milica M",
                "phone": "+38267123456",
                "email": "milica@example.com",
                "role_type": "buyer",
                "status": "active",
                "assigned_agent_id": agent["user_id"],
                "budget_min": "100000",
                "budget_max": "150000",
                "preferred_city": "Tivat",
                "preferred_property_type": "apartment",
                "notes": "",
            },
            actor_user_id=agent["user_id"],
        )
        property_row = self.context.property_service.create_record(
            {
                "title": "Marina View Apartment",
                "listing_type": "sale",
                "property_type": "apartment",
                "address": "Obala bb",
                "city": "Tivat",
                "area_sqm": "85",
                "rooms": "3",
                "bathrooms": "2",
                "floor": "4",
                "price": "145000",
                "currency": "EUR",
                "owner_client_id": client["client_id"],
                "assigned_agent_id": agent["user_id"],
                "status": "active",
                "commission_rate": "3",
                "description": "",
            },
            actor_user_id=agent["user_id"],
        )
        deal = self.context.deal_service.create_record(
            {
                "client_id": client["client_id"],
                "property_id": property_row["property_id"],
                "agent_id": agent["user_id"],
                "deal_type": "sale",
                "stage": "offer",
                "status": "open",
                "asking_price": "145000",
                "offer_price": "140000",
                "agreed_price": "142000",
                "commission_rate": "3",
                "commission_amount": "",
                "expected_close_date": "2026-05-01",
                "closed_date": "",
                "notes": "",
            },
            actor_user_id=agent["user_id"],
        )
        self.assertEqual(deal["commission_amount"], "4260.00")

    def test_client_delete_is_blocked_when_referenced(self) -> None:
        agent = self.context.user_service.list_records()[0]
        client = self.context.client_service.create_record(
            {
                "full_name": "Owner Client",
                "phone": "+38267123457",
                "email": "owner@example.com",
                "role_type": "seller",
                "status": "active",
                "assigned_agent_id": agent["user_id"],
                "budget_min": "",
                "budget_max": "",
                "preferred_city": "",
                "preferred_property_type": "",
                "notes": "",
            },
            actor_user_id=agent["user_id"],
        )
        self.context.property_service.create_record(
            {
                "title": "House with Garden",
                "listing_type": "sale",
                "property_type": "house",
                "address": "Njegoseva 10",
                "city": "Cetinje",
                "area_sqm": "180",
                "rooms": "5",
                "bathrooms": "2",
                "floor": "1",
                "price": "220000",
                "currency": "EUR",
                "owner_client_id": client["client_id"],
                "assigned_agent_id": agent["user_id"],
                "status": "active",
                "commission_rate": "4",
                "description": "",
            },
            actor_user_id=agent["user_id"],
        )
        with self.assertRaises(ValidationError):
            self.context.client_service.delete_record(client["client_id"], actor_user_id=agent["user_id"])
