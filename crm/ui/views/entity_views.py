from __future__ import annotations

from crm.config import as_choices
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
from crm.ui.dialogs import FieldSpec
from crm.ui.views.base_entity_view import BaseEntityView, FilterSpec


def enum_options(values) -> list[tuple[str, str]]:
    return [(value, value.replace("_", " ").title()) for value in as_choices(values)]


class _LookupMixin:
    def agent_options(self) -> list[tuple[str, str]]:
        return [
            (row["user_id"], f"{row['full_name']} ({row['username']})")
            for row in self.shell.context.user_service.list_records()
            if row.get("is_active") == "1"
        ]

    def client_options(self) -> list[tuple[str, str]]:
        return [
            (row["client_id"], f"{row['full_name']} [{row['role_type']}]")
            for row in self.shell.context.client_service.list_records()
        ]

    def property_options(self) -> list[tuple[str, str]]:
        return [
            (row["property_id"], f"{row['title']} | {row['city']}")
            for row in self.shell.context.property_service.list_records()
        ]

    def deal_options(self) -> list[tuple[str, str]]:
        return [
            (row["deal_id"], f"{row['deal_id']} | {row['stage']}")
            for row in self.shell.context.deal_service.list_records()
        ]


class UsersView(_LookupMixin, BaseEntityView):
    title = "Users"
    singular_title = "User"

    def build_filters(self) -> list[FilterSpec]:
        return [
            FilterSpec("role", "Role", enum_options(Role)),
            FilterSpec("is_active", "Status", [("1", "Active"), ("0", "Inactive")]),
        ]

    def build_form_fields(self, record: dict[str, str] | None = None) -> list[FieldSpec]:
        password_required = record is None
        return [
            FieldSpec("username", "Username", required=True),
            FieldSpec("full_name", "Full Name", required=True),
            FieldSpec("role", "Role", widget_type="combo", options=enum_options(Role), required=True),
            FieldSpec("phone", "Phone"),
            FieldSpec("email", "Email"),
            FieldSpec("password", "Password", widget_type="password", required=password_required),
            FieldSpec("is_active", "Status", widget_type="combo", options=[("1", "Active"), ("0", "Inactive")], required=True),
        ]


class ClientsView(_LookupMixin, BaseEntityView):
    title = "Clients"
    singular_title = "Client"

    def build_filters(self) -> list[FilterSpec]:
        return [
            FilterSpec("role_type", "Type", enum_options(ClientRoleType)),
            FilterSpec("status", "Status", enum_options(ClientStatus)),
        ]

    def build_form_fields(self, record: dict[str, str] | None = None) -> list[FieldSpec]:
        return [
            FieldSpec("full_name", "Full Name", required=True),
            FieldSpec("phone", "Phone"),
            FieldSpec("email", "Email"),
            FieldSpec("role_type", "Client Type", widget_type="combo", options=enum_options(ClientRoleType), required=True),
            FieldSpec("status", "Status", widget_type="combo", options=enum_options(ClientStatus), required=True),
            FieldSpec("assigned_agent_id", "Assigned Agent", widget_type="combo", options=[("", "Unassigned")] + self.agent_options()),
            FieldSpec("budget_min", "Budget Min"),
            FieldSpec("budget_max", "Budget Max"),
            FieldSpec("preferred_city", "Preferred City"),
            FieldSpec("preferred_property_type", "Preferred Property Type"),
            FieldSpec("notes", "Notes", widget_type="textbox"),
        ]


class PropertiesView(_LookupMixin, BaseEntityView):
    title = "Properties"
    singular_title = "Property"

    def build_filters(self) -> list[FilterSpec]:
        return [
            FilterSpec("listing_type", "Listing", enum_options(ListingType)),
            FilterSpec("property_type", "Property Type", enum_options(PropertyType)),
            FilterSpec("status", "Status", enum_options(PropertyStatus)),
        ]

    def build_form_fields(self, record: dict[str, str] | None = None) -> list[FieldSpec]:
        return [
            FieldSpec("title", "Title", required=True),
            FieldSpec("listing_type", "Listing Type", widget_type="combo", options=enum_options(ListingType), required=True),
            FieldSpec("property_type", "Property Type", widget_type="combo", options=enum_options(PropertyType), required=True),
            FieldSpec("address", "Address", required=True),
            FieldSpec("city", "City", required=True),
            FieldSpec("area_sqm", "Area (sqm)"),
            FieldSpec("rooms", "Rooms"),
            FieldSpec("bathrooms", "Bathrooms"),
            FieldSpec("floor", "Floor"),
            FieldSpec("price", "Price"),
            FieldSpec("currency", "Currency"),
            FieldSpec("owner_client_id", "Owner", widget_type="combo", options=[("", "Not linked")] + self.client_options()),
            FieldSpec("assigned_agent_id", "Assigned Agent", widget_type="combo", options=[("", "Unassigned")] + self.agent_options()),
            FieldSpec("status", "Status", widget_type="combo", options=enum_options(PropertyStatus), required=True),
            FieldSpec("commission_rate", "Commission Rate (%)"),
            FieldSpec("description", "Description", widget_type="textbox"),
        ]


class DealsView(_LookupMixin, BaseEntityView):
    title = "Deals"
    singular_title = "Deal"

    def build_filters(self) -> list[FilterSpec]:
        return [
            FilterSpec("stage", "Stage", enum_options(DealStage)),
            FilterSpec("status", "Status", enum_options(DealStatus)),
            FilterSpec("deal_type", "Type", enum_options(DealType)),
        ]

    def build_form_fields(self, record: dict[str, str] | None = None) -> list[FieldSpec]:
        return [
            FieldSpec("client_id", "Client", widget_type="combo", options=self.client_options(), required=True),
            FieldSpec("property_id", "Property", widget_type="combo", options=self.property_options(), required=True),
            FieldSpec("agent_id", "Agent", widget_type="combo", options=self.agent_options(), required=True),
            FieldSpec("deal_type", "Deal Type", widget_type="combo", options=enum_options(DealType), required=True),
            FieldSpec("stage", "Stage", widget_type="combo", options=enum_options(DealStage), required=True),
            FieldSpec("status", "Status", widget_type="combo", options=enum_options(DealStatus), required=True),
            FieldSpec("asking_price", "Asking Price"),
            FieldSpec("offer_price", "Offer Price"),
            FieldSpec("agreed_price", "Agreed Price"),
            FieldSpec("commission_rate", "Commission Rate (%)"),
            FieldSpec("commission_amount", "Commission Amount"),
            FieldSpec("expected_close_date", "Expected Close Date"),
            FieldSpec("closed_date", "Closed Date"),
            FieldSpec("notes", "Notes", widget_type="textbox"),
        ]


class AppointmentsView(_LookupMixin, BaseEntityView):
    title = "Appointments"
    singular_title = "Appointment"

    def build_filters(self) -> list[FilterSpec]:
        return [FilterSpec("status", "Status", enum_options(AppointmentStatus))]

    def build_form_fields(self, record: dict[str, str] | None = None) -> list[FieldSpec]:
        return [
            FieldSpec("title", "Title", required=True),
            FieldSpec("client_id", "Client", widget_type="combo", options=self.client_options(), required=True),
            FieldSpec("property_id", "Property", widget_type="combo", options=[("", "Not linked")] + self.property_options()),
            FieldSpec("agent_id", "Agent", widget_type="combo", options=self.agent_options(), required=True),
            FieldSpec("appointment_date", "Date (YYYY-MM-DD)", required=True),
            FieldSpec("appointment_time", "Time (HH:MM)", required=True),
            FieldSpec("location", "Location", required=True),
            FieldSpec("status", "Status", widget_type="combo", options=enum_options(AppointmentStatus), required=True),
            FieldSpec("notes", "Notes", widget_type="textbox"),
        ]


class TasksView(_LookupMixin, BaseEntityView):
    title = "Tasks"
    singular_title = "Task"

    def build_filters(self) -> list[FilterSpec]:
        return [
            FilterSpec("status", "Status", enum_options(TaskStatus)),
            FilterSpec("priority", "Priority", enum_options(TaskPriority)),
        ]

    def build_form_fields(self, record: dict[str, str] | None = None) -> list[FieldSpec]:
        return [
            FieldSpec("title", "Title", required=True),
            FieldSpec("related_entity_type", "Related Type", widget_type="combo", options=enum_options(RelatedEntityType), required=True),
            FieldSpec("related_entity_id", "Related Entity ID"),
            FieldSpec("assigned_agent_id", "Assigned Agent", widget_type="combo", options=self.agent_options(), required=True),
            FieldSpec("due_date", "Due Date (YYYY-MM-DD)", required=True),
            FieldSpec("priority", "Priority", widget_type="combo", options=enum_options(TaskPriority), required=True),
            FieldSpec("status", "Status", widget_type="combo", options=enum_options(TaskStatus), required=True),
            FieldSpec("notes", "Notes", widget_type="textbox"),
        ]


class InteractionsView(_LookupMixin, BaseEntityView):
    title = "Interactions"
    singular_title = "Interaction"

    def build_filters(self) -> list[FilterSpec]:
        return [FilterSpec("interaction_type", "Type", enum_options(InteractionType))]

    def build_form_fields(self, record: dict[str, str] | None = None) -> list[FieldSpec]:
        return [
            FieldSpec("interaction_type", "Interaction Type", widget_type="combo", options=enum_options(InteractionType), required=True),
            FieldSpec("client_id", "Client", widget_type="combo", options=[("", "Not linked")] + self.client_options()),
            FieldSpec("property_id", "Property", widget_type="combo", options=[("", "Not linked")] + self.property_options()),
            FieldSpec("deal_id", "Deal", widget_type="combo", options=[("", "Not linked")] + self.deal_options()),
            FieldSpec("agent_id", "Agent", widget_type="combo", options=self.agent_options(), required=True),
            FieldSpec("interaction_datetime", "Datetime (YYYY-MM-DDTHH:MM)", required=True),
            FieldSpec("subject", "Subject", required=True),
            FieldSpec("summary", "Summary", widget_type="textbox", required=True),
            FieldSpec("next_step", "Next Step", widget_type="textbox"),
        ]
