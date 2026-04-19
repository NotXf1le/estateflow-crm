from __future__ import annotations

import customtkinter as ctk

from crm.formatters import format_currency
from crm.ui.components.cards import KpiCard


class DashboardView(ctk.CTkFrame):
    def __init__(self, master, *, on_quick_action) -> None:
        super().__init__(master, fg_color="transparent")
        self.on_quick_action = on_quick_action
        self.grid_columnconfigure((0, 1, 2), weight=1, uniform="dash")
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self.cards: dict[str, KpiCard] = {}
        card_specs = [
            ("total_clients", "Clients", "#2F7BFF"),
            ("active_listings", "Active Listings", "#23B26D"),
            ("open_deals", "Open Deals", "#F59E0B"),
            ("scheduled_appointments", "Appointments", "#12B7D5"),
            ("overdue_tasks", "Overdue Tasks", "#E85B5B"),
            ("projected_commission", "Projected Commission", "#A855F7"),
        ]
        for index, (key, title, accent) in enumerate(card_specs):
            card = KpiCard(self, title=title, value="0", accent=accent)
            card.grid(row=index // 3, column=index % 3, sticky="nsew", padx=10, pady=10)
            self.cards[key] = card

        quick_actions = ctk.CTkFrame(self, fg_color=("white", "#1E2740"), corner_radius=18)
        quick_actions.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
        quick_actions.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            quick_actions,
            text="Quick Actions",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=18, pady=(18, 12))
        actions = [
            ("New client", "clients"),
            ("New listing", "properties"),
            ("New deal", "deals"),
            ("New appointment", "appointments"),
            ("New task", "tasks"),
            ("New note", "interactions"),
        ]
        for row_index, (label, key) in enumerate(actions, start=1):
            button = ctk.CTkButton(
                quick_actions,
                text=label,
                anchor="w",
                fg_color="transparent",
                border_width=1,
                command=lambda target=key: self.on_quick_action(target),
            )
            button.grid(row=row_index, column=0, sticky="ew", padx=18, pady=6)

        self.recent_activity = self._build_text_panel("Recent Activity")
        self.recent_activity.grid(row=2, column=1, columnspan=2, sticky="nsew", padx=10, pady=10)
        self.upcoming_panel = self._build_text_panel("Upcoming Appointments")
        self.upcoming_panel.grid(row=3, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)
        self.stage_panel = self._build_text_panel("Deals by Stage")
        self.stage_panel.grid(row=3, column=2, sticky="nsew", padx=10, pady=10)

    def _build_text_panel(self, title: str) -> ctk.CTkFrame:
        panel = ctk.CTkFrame(self, fg_color=("white", "#1E2740"), corner_radius=18)
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(1, weight=1)
        header = ctk.CTkLabel(panel, text=title, font=ctk.CTkFont(size=18, weight="bold"))
        header.grid(row=0, column=0, sticky="w", padx=18, pady=(18, 12))
        textbox = ctk.CTkTextbox(panel, corner_radius=12)
        textbox.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 18))
        textbox.configure(state="disabled")
        panel.textbox = textbox
        return panel

    def _set_text(self, panel: ctk.CTkFrame, lines: list[str]) -> None:
        textbox = panel.textbox
        textbox.configure(state="normal")
        textbox.delete("1.0", "end")
        textbox.insert("1.0", "\n".join(lines) if lines else "No data available.")
        textbox.configure(state="disabled")

    def refresh(self, data: dict[str, object]) -> None:
        kpis = data.get("kpis", {})
        self.cards["total_clients"].update_value(str(kpis.get("total_clients", 0)))
        self.cards["active_listings"].update_value(str(kpis.get("active_listings", 0)))
        self.cards["open_deals"].update_value(str(kpis.get("open_deals", 0)))
        self.cards["scheduled_appointments"].update_value(str(kpis.get("scheduled_appointments", 0)))
        self.cards["overdue_tasks"].update_value(str(kpis.get("overdue_tasks", 0)))
        self.cards["projected_commission"].update_value(format_currency(str(kpis.get("projected_commission", "0"))))

        activity_lines = [
            f"{row.get('created_at', '')} | {row.get('action', '').upper()} | {row.get('entity_type', '')} | {row.get('details', '')}"
            for row in data.get("recent_activity", [])
        ]
        appointment_lines = [
            f"{row.get('appointment_date', '')} {row.get('appointment_time', '')} | {row.get('title', '')} | {row.get('status', '')}"
            for row in data.get("upcoming_appointments", [])
        ]
        stage_lines = [
            f"{stage}: {count}"
            for stage, count in sorted(data.get("deals_by_stage", {}).items())
        ]
        self._set_text(self.recent_activity, activity_lines)
        self._set_text(self.upcoming_panel, appointment_lines)
        self._set_text(self.stage_panel, stage_lines)
