from __future__ import annotations

from decimal import Decimal

from crm.config import DATA_DIR
from crm.enums import AuditAction
from crm.services.appointment_service import AppointmentService
from crm.services.audit_service import AuditService
from crm.services.client_service import ClientService
from crm.services.deal_service import DealService
from crm.services.interaction_service import InteractionService
from crm.services.property_service import PropertyService
from crm.services.task_service import TaskService
from crm.services.user_service import UserService
from crm.utils import ensure_backup_snapshot, parse_decimal


class ReportService:
    def __init__(
        self,
        *,
        user_service: UserService,
        client_service: ClientService,
        property_service: PropertyService,
        deal_service: DealService,
        appointment_service: AppointmentService,
        task_service: TaskService,
        interaction_service: InteractionService,
        audit_service: AuditService,
    ) -> None:
        self.user_service = user_service
        self.client_service = client_service
        self.property_service = property_service
        self.deal_service = deal_service
        self.appointment_service = appointment_service
        self.task_service = task_service
        self.interaction_service = interaction_service
        self.audit_service = audit_service

    def dashboard_summary(self) -> dict[str, object]:
        clients = self.client_service.list_records()
        properties = self.property_service.list_records(filters={"status": "active"})
        deals = self.deal_service.list_records(filters={"status": "open"})
        all_upcoming = self.appointment_service.upcoming(limit=9999)
        appointments = all_upcoming[:8]
        tasks = self.task_service.list_records(filters={"status": "overdue"})
        pipeline = self.deal_service.list_records()
        projected_commission = sum(
            parse_decimal(item.get("commission_amount", ""), Decimal("0")) or Decimal("0")
            for item in pipeline
            if item.get("status") != "lost"
        )
        stage_summary: dict[str, int] = {}
        for row in pipeline:
            stage_summary[row["stage"]] = stage_summary.get(row["stage"], 0) + 1
        return {
            "kpis": {
                "total_clients": len(clients),
                "active_listings": len(properties),
                "open_deals": len(deals),
                "scheduled_appointments": len(all_upcoming),
                "overdue_tasks": len(tasks),
                "projected_commission": f"{projected_commission:.2f}",
            },
            "recent_activity": self.audit_service.recent(limit=12),
            "upcoming_appointments": appointments,
            "deals_by_stage": stage_summary,
        }

    def deals_by_stage(self) -> list[dict[str, str]]:
        summary: dict[str, int] = {}
        for row in self.deal_service.list_records():
            summary[row["stage"]] = summary.get(row["stage"], 0) + 1
        return [{"stage": stage, "count": str(count)} for stage, count in sorted(summary.items())]

    def revenue_summary(self) -> list[dict[str, str]]:
        won = [row for row in self.deal_service.list_records() if row.get("status") == "won"]
        total_value = sum(parse_decimal(row.get("agreed_price", ""), Decimal("0")) or Decimal("0") for row in won)
        total_commission = sum(parse_decimal(row.get("commission_amount", ""), Decimal("0")) or Decimal("0") for row in won)
        return [
            {"metric": "Closed deals", "value": str(len(won))},
            {"metric": "Closed value", "value": f"{total_value:.2f}"},
            {"metric": "Commission earned", "value": f"{total_commission:.2f}"},
        ]

    def active_listings_by_city_type(self) -> list[dict[str, str]]:
        summary: dict[tuple[str, str], int] = {}
        for row in self.property_service.list_records(filters={"status": "active"}):
            key = (row.get("city", "-"), row.get("property_type", "-"))
            summary[key] = summary.get(key, 0) + 1
        return [
            {"city": city, "property_type": property_type, "count": str(count)}
            for (city, property_type), count in sorted(summary.items())
        ]

    def overdue_tasks_by_agent(self) -> list[dict[str, str]]:
        agent_lookup = {row["user_id"]: row["full_name"] for row in self.user_service.list_records()}
        summary: dict[str, int] = {}
        for row in self.task_service.list_records(filters={"status": "overdue"}):
            summary[row["assigned_agent_id"]] = summary.get(row["assigned_agent_id"], 0) + 1
        return [
            {"agent": agent_lookup.get(agent_id, agent_id), "count": str(count)}
            for agent_id, count in sorted(summary.items(), key=lambda item: item[1], reverse=True)
        ]

    def appointments_by_status(self) -> list[dict[str, str]]:
        summary: dict[str, int] = {}
        for row in self.appointment_service.list_records():
            summary[row["status"]] = summary.get(row["status"], 0) + 1
        return [{"status": status, "count": str(count)} for status, count in sorted(summary.items())]

    def available_reports(self) -> dict[str, callable]:
        return {
            "Deals by stage": self.deals_by_stage,
            "Revenue summary": self.revenue_summary,
            "Active listings by city/type": self.active_listings_by_city_type,
            "Overdue tasks by agent": self.overdue_tasks_by_agent,
            "Appointments by status": self.appointments_by_status,
        }

    def build_report(self, report_name: str) -> list[dict[str, str]]:
        reports = self.available_reports()
        if report_name not in reports:
            return []
        return reports[report_name]()

    def create_backup(self, actor_user_id: str = "") -> str:
        backup_path = ensure_backup_snapshot(DATA_DIR)
        self.audit_service.log(
            actor_user_id=actor_user_id,
            entity_type="system",
            entity_id="backup",
            action=AuditAction.BACKUP,
            details=f"Backup created at {backup_path.name}",
        )
        return str(backup_path)
