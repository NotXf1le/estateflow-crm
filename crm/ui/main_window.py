from __future__ import annotations

import customtkinter as ctk

from crm.config import APP_NAME, APP_VERSION
from crm.enums import Role
from crm.ui.theme import apply_ttk_theme
from crm.ui.views.dashboard_view import DashboardView
from crm.ui.views.entity_views import (
    AppointmentsView,
    ClientsView,
    DealsView,
    InteractionsView,
    PropertiesView,
    TasksView,
    UsersView,
)
from crm.ui.views.login_view import LoginView
from crm.ui.views.reports_view import ReportsView
from crm.validators import ValidationError


class MainShell(ctk.CTkFrame):
    def __init__(self, master, *, context, current_user: dict[str, str], on_logout) -> None:
        super().__init__(master, fg_color="transparent")
        self.context = context
        self.current_user = current_user
        self.on_logout = on_logout
        self.active_view_key = "dashboard"
        self.views: dict[str, ctk.CTkFrame] = {}

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        topbar = ctk.CTkFrame(self, corner_radius=0, fg_color=("white", "#121B2B"))
        topbar.grid(row=0, column=0, sticky="ew")
        topbar.grid_columnconfigure(1, weight=1)
        self.title_label = ctk.CTkLabel(topbar, text="Dashboard", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.grid(row=0, column=0, sticky="w", padx=24, pady=16)
        user_label = ctk.CTkLabel(topbar, text=f"{current_user['full_name']} | {current_user['role']}")
        user_label.grid(row=0, column=1, sticky="e", padx=(0, 16), pady=16)
        theme_selector = ctk.CTkComboBox(topbar, values=["Light", "Dark", "System"], width=120, state="readonly", command=self._set_theme)
        theme_selector.grid(row=0, column=2, padx=(0, 10), pady=16)
        theme_selector.set(ctk.get_appearance_mode())
        logout_button = ctk.CTkButton(topbar, text="Logout", width=110, fg_color="transparent", border_width=1, command=self.on_logout)
        logout_button.grid(row=0, column=3, padx=(0, 24), pady=16)

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.grid(row=1, column=0, sticky="nsew")
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(0, weight=1)

        sidebar = ctk.CTkFrame(body, width=220, corner_radius=0, fg_color=("#E9EEF9", "#0F172A"))
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_columnconfigure(0, weight=1)
        sidebar.grid_rowconfigure(99, weight=1)
        brand = ctk.CTkLabel(
            sidebar,
            text=f"{APP_NAME}\nv{APP_VERSION}",
            justify="left",
            font=ctk.CTkFont(size=20, weight="bold"),
            anchor="w",
        )
        brand.grid(row=0, column=0, sticky="w", padx=18, pady=(18, 28))

        nav_items = [
            ("dashboard", "Dashboard"),
            ("clients", "Clients"),
            ("properties", "Properties"),
            ("deals", "Deals"),
            ("appointments", "Appointments"),
            ("tasks", "Tasks"),
            ("interactions", "Interactions"),
            ("reports", "Reports"),
        ]
        if current_user["role"] == Role.ADMIN.value:
            nav_items.append(("users", "Users"))
        self.nav_buttons: dict[str, ctk.CTkButton] = {}
        for row_index, (key, label) in enumerate(nav_items, start=1):
            button = ctk.CTkButton(
                sidebar,
                text=label,
                anchor="w",
                fg_color="transparent",
                hover_color=("#D5E1FF", "#19233A"),
                command=lambda target=key: self.navigate(target),
            )
            button.grid(row=row_index, column=0, sticky="ew", padx=14, pady=4)
            self.nav_buttons[key] = button

        content = ctk.CTkFrame(body, fg_color="transparent")
        content.grid(row=0, column=1, sticky="nsew")
        content.grid_columnconfigure(0, weight=1)
        content.grid_rowconfigure(0, weight=1)
        self.content = content

        status_bar = ctk.CTkFrame(self, corner_radius=0, fg_color=("white", "#121B2B"))
        status_bar.grid(row=2, column=0, sticky="ew")
        status_bar.grid_columnconfigure(0, weight=1)
        self.status_label = ctk.CTkLabel(status_bar, text="Ready", anchor="w")
        self.status_label.grid(row=0, column=0, sticky="ew", padx=18, pady=8)

        self._build_views()
        self.navigate("dashboard")

    def _build_views(self) -> None:
        self.views["dashboard"] = DashboardView(self.content, on_quick_action=self.open_quick_action)
        self.views["clients"] = ClientsView(
            self.content,
            shell=self,
            service=self.context.client_service,
            columns=[
                ("client_id", "ID", 150),
                ("full_name", "Name", 180),
                ("role_type", "Type", 110),
                ("status", "Status", 100),
                ("phone", "Phone", 120),
                ("preferred_city", "City", 120),
                ("assigned_agent_id", "Agent", 150),
            ],
        )
        self.views["properties"] = PropertiesView(
            self.content,
            shell=self,
            service=self.context.property_service,
            columns=[
                ("property_id", "ID", 150),
                ("title", "Title", 200),
                ("listing_type", "Listing", 90),
                ("property_type", "Type", 100),
                ("city", "City", 120),
                ("price", "Price", 120),
                ("status", "Status", 100),
            ],
        )
        self.views["deals"] = DealsView(
            self.content,
            shell=self,
            service=self.context.deal_service,
            columns=[
                ("deal_id", "ID", 150),
                ("client_id", "Client", 150),
                ("property_id", "Property", 150),
                ("stage", "Stage", 120),
                ("status", "Status", 100),
                ("agreed_price", "Agreed", 110),
                ("commission_amount", "Commission", 120),
            ],
        )
        self.views["appointments"] = AppointmentsView(
            self.content,
            shell=self,
            service=self.context.appointment_service,
            columns=[
                ("appointment_id", "ID", 150),
                ("title", "Title", 180),
                ("appointment_date", "Date", 110),
                ("appointment_time", "Time", 90),
                ("status", "Status", 100),
                ("location", "Location", 180),
            ],
        )
        self.views["tasks"] = TasksView(
            self.content,
            shell=self,
            service=self.context.task_service,
            columns=[
                ("task_id", "ID", 150),
                ("title", "Title", 220),
                ("priority", "Priority", 100),
                ("status", "Status", 100),
                ("due_date", "Due Date", 110),
                ("assigned_agent_id", "Agent", 150),
            ],
        )
        self.views["interactions"] = InteractionsView(
            self.content,
            shell=self,
            service=self.context.interaction_service,
            columns=[
                ("interaction_id", "ID", 150),
                ("interaction_type", "Type", 110),
                ("subject", "Subject", 220),
                ("interaction_datetime", "Datetime", 160),
                ("agent_id", "Agent", 150),
            ],
        )
        self.views["reports"] = ReportsView(self.content, shell=self, report_service=self.context.report_service)
        if self.current_user["role"] == Role.ADMIN.value:
            self.views["users"] = UsersView(
                self.content,
                shell=self,
                service=self.context.user_service,
                columns=[
                    ("user_id", "ID", 150),
                    ("username", "Username", 130),
                    ("full_name", "Full Name", 180),
                    ("role", "Role", 100),
                    ("email", "Email", 180),
                    ("is_active", "Active", 80),
                ],
            )

        for view in self.views.values():
            view.grid(row=0, column=0, sticky="nsew")
            view.grid_remove()

    def _set_theme(self, mode: str) -> None:
        ctk.set_appearance_mode(mode)
        apply_ttk_theme(self, mode)

    def set_status(self, message: str) -> None:
        self.status_label.configure(text=message)

    def navigate(self, key: str) -> None:
        for view_key, view in self.views.items():
            if view_key == key:
                view.grid()
            else:
                view.grid_remove()
        self.active_view_key = key
        self.title_label.configure(text=self.nav_buttons.get(key).cget("text") if key in self.nav_buttons else key.title())
        if key == "dashboard":
            self.views["dashboard"].refresh(self.context.report_service.dashboard_summary())
        elif key == "reports":
            self.views["reports"]._reload_report()
        elif hasattr(self.views[key], "reload"):
            self.views[key].reload()
        for button_key, button in self.nav_buttons.items():
            button.configure(fg_color=("#D7E2FF", "#18233A") if button_key == key else "transparent")

    def open_quick_action(self, key: str) -> None:
        self.navigate(key)
        view = self.views.get(key)
        if hasattr(view, "open_create_dialog"):
            view.open_create_dialog()


class CRMApplication(ctk.CTk):
    def __init__(self, context) -> None:
        super().__init__()
        self.context = context
        self.current_user: dict[str, str] | None = None
        self.title(APP_NAME)
        self.geometry("1600x920")
        self.minsize(1280, 780)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        apply_ttk_theme(self)
        self.show_login()

    def show_login(self) -> None:
        self.current_user = None
        for child in self.winfo_children():
            child.destroy()
        login = LoginView(self, on_login=self.handle_login)
        login.grid(row=0, column=0, sticky="nsew")
        self.login_view = login

    def handle_login(self, username: str, password: str) -> None:
        try:
            user = self.context.auth_service.login(username, password)
        except ValidationError as error:
            self.login_view.set_error(str(error))
            return
        self.current_user = user
        for child in self.winfo_children():
            child.destroy()
        shell = MainShell(self, context=self.context, current_user=user, on_logout=self.show_login)
        shell.grid(row=0, column=0, sticky="nsew")
        self.shell = shell
