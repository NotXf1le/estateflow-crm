from __future__ import annotations

import logging
from dataclasses import dataclass

from crm.config import APP_LOG_FILE, ensure_directories
from crm.repositories.appointments_repository import AppointmentsRepository
from crm.repositories.audit_repository import AuditRepository
from crm.repositories.clients_repository import ClientsRepository
from crm.repositories.deals_repository import DealsRepository
from crm.repositories.interactions_repository import InteractionsRepository
from crm.repositories.properties_repository import PropertiesRepository
from crm.repositories.tasks_repository import TasksRepository
from crm.repositories.users_repository import UsersRepository
from crm.services.appointment_service import AppointmentService
from crm.services.audit_service import AuditService
from crm.services.auth_service import AuthService
from crm.services.client_service import ClientService
from crm.services.deal_service import DealService
from crm.services.interaction_service import InteractionService
from crm.services.property_service import PropertyService
from crm.services.report_service import ReportService
from crm.services.task_service import TaskService
from crm.services.user_service import UserService
from crm.ui.main_window import CRMApplication
from crm.ui.theme import initialize_theme


@dataclass
class AppContext:
    auth_service: AuthService
    user_service: UserService
    client_service: ClientService
    property_service: PropertyService
    deal_service: DealService
    appointment_service: AppointmentService
    task_service: TaskService
    interaction_service: InteractionService
    report_service: ReportService
    audit_service: AuditService


def configure_logging() -> None:
    ensure_directories()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        handlers=[
            logging.FileHandler(APP_LOG_FILE, encoding="utf-8"),
        ],
        force=True,
    )


def build_context() -> AppContext:
    ensure_directories()
    users_repository = UsersRepository()
    clients_repository = ClientsRepository()
    properties_repository = PropertiesRepository()
    deals_repository = DealsRepository()
    appointments_repository = AppointmentsRepository()
    tasks_repository = TasksRepository()
    interactions_repository = InteractionsRepository()
    audit_repository = AuditRepository()

    audit_service = AuditService(audit_repository)
    auth_service = AuthService(users_repository, audit_service)
    auth_service.ensure_default_admin()

    user_service = UserService(
        users_repository,
        audit_service,
        auth_service,
        clients_repository=clients_repository,
        properties_repository=properties_repository,
        deals_repository=deals_repository,
        appointments_repository=appointments_repository,
        tasks_repository=tasks_repository,
        interactions_repository=interactions_repository,
    )
    client_service = ClientService(
        clients_repository,
        audit_service,
        users_repository=users_repository,
        properties_repository=properties_repository,
        deals_repository=deals_repository,
        appointments_repository=appointments_repository,
        tasks_repository=tasks_repository,
        interactions_repository=interactions_repository,
    )
    property_service = PropertyService(
        properties_repository,
        audit_service,
        users_repository=users_repository,
        clients_repository=clients_repository,
        deals_repository=deals_repository,
        appointments_repository=appointments_repository,
        tasks_repository=tasks_repository,
        interactions_repository=interactions_repository,
    )
    deal_service = DealService(
        deals_repository,
        audit_service,
        users_repository=users_repository,
        clients_repository=clients_repository,
        properties_repository=properties_repository,
        tasks_repository=tasks_repository,
        interactions_repository=interactions_repository,
    )
    appointment_service = AppointmentService(
        appointments_repository,
        audit_service,
        users_repository=users_repository,
        clients_repository=clients_repository,
        properties_repository=properties_repository,
    )
    task_service = TaskService(
        tasks_repository,
        audit_service,
        users_repository=users_repository,
        clients_repository=clients_repository,
        properties_repository=properties_repository,
        deals_repository=deals_repository,
    )
    interaction_service = InteractionService(
        interactions_repository,
        audit_service,
        users_repository=users_repository,
        clients_repository=clients_repository,
        properties_repository=properties_repository,
        deals_repository=deals_repository,
    )
    report_service = ReportService(
        user_service=user_service,
        client_service=client_service,
        property_service=property_service,
        deal_service=deal_service,
        appointment_service=appointment_service,
        task_service=task_service,
        interaction_service=interaction_service,
        audit_service=audit_service,
    )
    return AppContext(
        auth_service=auth_service,
        user_service=user_service,
        client_service=client_service,
        property_service=property_service,
        deal_service=deal_service,
        appointment_service=appointment_service,
        task_service=task_service,
        interaction_service=interaction_service,
        report_service=report_service,
        audit_service=audit_service,
    )


def create_application() -> CRMApplication:
    configure_logging()
    initialize_theme()
    context = build_context()
    return CRMApplication(context)
