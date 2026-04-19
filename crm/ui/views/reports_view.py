from __future__ import annotations

from pathlib import Path
from tkinter import filedialog

import customtkinter as ctk

from crm.config import EXPORT_DIR
from crm.ui.components.table import TableWidget
from crm.ui.dialogs import show_info


class ReportsView(ctk.CTkFrame):
    def __init__(self, master, *, shell, report_service) -> None:
        super().__init__(master, fg_color="transparent")
        self.shell = shell
        self.report_service = report_service
        self.current_report_name = "Deals by stage"
        self.current_rows: list[dict[str, str]] = []

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        controls = ctk.CTkFrame(self, fg_color=("white", "#1E2740"), corner_radius=18)
        controls.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 8))
        controls.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(controls, text="Report", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, sticky="w", padx=(16, 10), pady=16)
        self.report_names = list(self.report_service.available_reports().keys())
        self.report_selector = ctk.CTkComboBox(
            controls,
            values=self.report_names,
            state="readonly",
            command=self._reload_report,
        )
        self.report_selector.grid(row=0, column=1, sticky="ew", padx=(0, 10), pady=16)
        self.report_selector.set(self.current_report_name)
        ctk.CTkButton(controls, text="Export Report", command=self.export_report).grid(row=0, column=2, padx=(0, 10), pady=16)
        ctk.CTkButton(controls, text="Create Backup", fg_color="transparent", border_width=1, command=self.create_backup).grid(row=0, column=3, padx=(0, 16), pady=16)

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        body.grid_columnconfigure(0, weight=2)
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(0, weight=1)

        self.table_card = ctk.CTkFrame(body, fg_color=("white", "#1E2740"), corner_radius=18)
        self.table_card.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        self.table_card.grid_columnconfigure(0, weight=1)
        self.table_card.grid_rowconfigure(0, weight=1)
        self.table = TableWidget(self.table_card, columns=[("metric", "Metric", 220), ("value", "Value", 180)])
        self.table.grid(row=0, column=0, sticky="nsew", padx=14, pady=14)

        self.summary_card = ctk.CTkFrame(body, fg_color=("white", "#1E2740"), corner_radius=18)
        self.summary_card.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        self.summary_card.grid_columnconfigure(0, weight=1)
        self.summary_card.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(self.summary_card, text="Report Notes", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, sticky="w", padx=16, pady=(16, 10))
        self.summary_text = ctk.CTkTextbox(self.summary_card)
        self.summary_text.grid(row=1, column=0, sticky="nsew", padx=16, pady=(0, 16))
        self.summary_text.configure(state="disabled")

    def _reload_report(self, _choice: str | None = None) -> None:
        self.current_report_name = self.report_selector.get()
        rows = self.report_service.build_report(self.current_report_name)
        if not rows:
            self.current_rows = []
            self.table.load_rows([], row_id_field="metric")
            return
        self.current_rows = rows
        columns = [(key, key.replace("_", " ").title(), 220) for key in rows[0].keys()]
        self.table.destroy()
        self.table = TableWidget(self.table_card, columns=columns)
        self.table.grid(row=0, column=0, sticky="nsew", padx=14, pady=14)
        row_id_field = list(rows[0].keys())[0]
        self.table.load_rows(rows, row_id_field=row_id_field)
        self.summary_text.configure(state="normal")
        self.summary_text.delete("1.0", "end")
        self.summary_text.insert(
            "1.0",
            f"Report: {self.current_report_name}\nRows: {len(rows)}\n\nUse Export Report to save the current summary as CSV.",
        )
        self.summary_text.configure(state="disabled")

    def export_report(self) -> None:
        if not self.current_rows:
            show_info("Export", "No report data is currently loaded.", parent=self)
            return
        target = filedialog.asksaveasfilename(
            parent=self,
            initialdir=EXPORT_DIR,
            initialfile=self.current_report_name.lower().replace(" ", "_") + ".csv",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
        )
        if not target:
            return
        import csv

        with Path(target).open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(self.current_rows[0].keys()))
            writer.writeheader()
            writer.writerows(self.current_rows)
        self.shell.set_status(f"Exported report: {self.current_report_name}.")
        show_info("Export complete", f"Saved to:\n{target}", parent=self)

    def create_backup(self) -> None:
        backup_path = self.report_service.create_backup(actor_user_id=self.shell.current_user["user_id"])
        self.shell.set_status(f"Backup created: {backup_path}")
        show_info("Backup created", backup_path, parent=self)
