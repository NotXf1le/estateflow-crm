from __future__ import annotations

import tkinter as tk
from dataclasses import dataclass, field
from pathlib import Path
from tkinter import filedialog

import customtkinter as ctk

from crm.config import EXPORT_DIR
from crm.ui.components.table import TableWidget
from crm.ui.dialogs import FieldSpec, RecordFormDialog, ask_confirmation, show_error, show_info
from crm.validators import ValidationError


@dataclass
class FilterSpec:
    key: str
    label: str
    options: list[tuple[str, str]] = field(default_factory=list)


class BaseEntityView(ctk.CTkFrame):
    title = "Records"
    singular_title = "Record"

    def __init__(self, master, *, shell, service, columns: list[tuple[str, str, int]]) -> None:
        super().__init__(master, fg_color="transparent")
        self.shell = shell
        self.service = service
        self.columns = columns
        self.sort_field = getattr(service, "sort_field", "")
        self.sort_reverse = False
        self.selected_id: str | None = None
        self.current_rows: list[dict[str, str]] = []

        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(1, weight=1)

        toolbar = ctk.CTkFrame(self, fg_color=("white", "#1E2740"), corner_radius=18)
        toolbar.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=(10, 8))
        toolbar.grid_columnconfigure(0, weight=1)

        top_controls = ctk.CTkFrame(toolbar, fg_color="transparent")
        top_controls.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 10))
        top_controls.grid_columnconfigure(0, weight=1)
        self.search_entry = ctk.CTkEntry(top_controls, placeholder_text=f"Search {self.title.lower()}...")
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", lambda _event: self.reload())

        self.filter_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        self.filter_frame.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 10))
        self.filter_frame.grid_columnconfigure(99, weight=1)
        self.filter_specs = self.build_filters()
        self.filter_vars: dict[str, tk.StringVar] = {}
        self.filter_boxes: dict[str, ctk.CTkComboBox] = {}
        self._build_filter_controls()

        buttons = ctk.CTkFrame(toolbar, fg_color="transparent")
        buttons.grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 16))
        for index in range(6):
            buttons.grid_columnconfigure(index, weight=1)
        ctk.CTkButton(buttons, text="New", command=self.open_create_dialog).grid(row=0, column=0, sticky="ew", padx=4)
        ctk.CTkButton(buttons, text="Edit", command=self.open_edit_dialog).grid(row=0, column=1, sticky="ew", padx=4)
        ctk.CTkButton(buttons, text="Delete", fg_color="#C44545", hover_color="#A33434", command=self.delete_selected).grid(row=0, column=2, sticky="ew", padx=4)
        ctk.CTkButton(buttons, text="Import CSV", fg_color="transparent", border_width=1, command=self.import_rows).grid(row=0, column=3, sticky="ew", padx=4)
        ctk.CTkButton(buttons, text="Export CSV", fg_color="transparent", border_width=1, command=self.export_rows).grid(row=0, column=4, sticky="ew", padx=4)
        ctk.CTkButton(buttons, text="Refresh", fg_color="transparent", border_width=1, command=self.reload).grid(row=0, column=5, sticky="ew", padx=4)

        table_card = ctk.CTkFrame(self, fg_color=("white", "#1E2740"), corner_radius=18)
        table_card.grid(row=1, column=0, sticky="nsew", padx=(10, 5), pady=(0, 10))
        table_card.grid_columnconfigure(0, weight=1)
        table_card.grid_rowconfigure(0, weight=1)
        self.table = TableWidget(table_card, columns=columns, on_sort=self.on_sort)
        self.table.grid(row=0, column=0, sticky="nsew", padx=14, pady=14)
        self.table.bind_select(self.handle_select)

        detail_card = ctk.CTkFrame(self, fg_color=("white", "#1E2740"), corner_radius=18)
        detail_card.grid(row=1, column=1, sticky="nsew", padx=(5, 10), pady=(0, 10))
        detail_card.grid_columnconfigure(0, weight=1)
        detail_card.grid_rowconfigure(1, weight=1)
        self.detail_title = ctk.CTkLabel(detail_card, text=f"{self.title} Details", font=ctk.CTkFont(size=20, weight="bold"))
        self.detail_title.grid(row=0, column=0, sticky="w", padx=16, pady=(16, 8))
        self.detail_text = ctk.CTkTextbox(detail_card)
        self.detail_text.grid(row=1, column=0, sticky="nsew", padx=16, pady=(0, 16))
        self.detail_text.configure(state="disabled")

    def build_filters(self) -> list[FilterSpec]:
        return []

    def build_form_fields(self, record: dict[str, str] | None = None) -> list[FieldSpec]:
        raise NotImplementedError

    def build_detail_text(self, record: dict[str, str]) -> str:
        labels = {field.key: field.label for field in self.build_form_fields(record)}
        ordered_fields = [column[0] for column in self.columns]
        lines = ["Selected record", ""]
        for key in ordered_fields:
            value = record.get(key, "")
            label = labels.get(key, key.replace("_", " ").title())
            lines.append(f"{label}: {value or '-'}")
        sections = self.service.detail_sections(record[self.service.id_field])
        for title, items in sections.items():
            lines.extend(["", title])
            lines.extend(f"- {item}" for item in items)
        return "\n".join(lines)

    def _build_filter_controls(self) -> None:
        for child in self.filter_frame.winfo_children():
            child.destroy()
        self.filter_boxes.clear()
        for index, spec in enumerate(self.filter_specs):
            label = ctk.CTkLabel(self.filter_frame, text=spec.label)
            label.grid(row=0, column=index * 2, sticky="w", padx=(0, 6))
            values = ["All"] + [label_text for _, label_text in spec.options]
            var = tk.StringVar(value="All")
            combo = ctk.CTkComboBox(
                self.filter_frame,
                values=values,
                variable=var,
                state="readonly",
                command=lambda _choice, key=spec.key: self.reload(),
            )
            combo.grid(row=0, column=index * 2 + 1, sticky="ew", padx=(0, 14))
            self.filter_vars[spec.key] = var
            self.filter_boxes[spec.key] = combo

    def refresh_filter_values(self) -> None:
        self.filter_specs = self.build_filters()
        self._build_filter_controls()

    def get_filters(self) -> dict[str, str]:
        filters: dict[str, str] = {}
        for spec in self.filter_specs:
            value = self.filter_vars[spec.key].get()
            if value == "All":
                continue
            label_to_value = {label: raw for raw, label in spec.options}
            filters[spec.key] = label_to_value.get(value, value)
        return filters

    def reload(self) -> None:
        self.current_rows = self.service.list_records(
            search_text=self.search_entry.get().strip(),
            filters=self.get_filters(),
            sort_field=self.sort_field,
            reverse=self.sort_reverse,
        )
        self.table.load_rows(self.current_rows, row_id_field=self.service.id_field)
        self.render_details()

    def on_sort(self, field: str) -> None:
        if self.sort_field == field:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_field = field
            self.sort_reverse = False
        self.reload()

    def handle_select(self) -> None:
        self.selected_id = self.table.selected_id()
        self.render_details()

    def render_details(self) -> None:
        record = None
        if self.selected_id:
            record = next((row for row in self.current_rows if row.get(self.service.id_field) == self.selected_id), None)
        if not record:
            text = f"No {self.title.lower()} selected."
        else:
            text = self.build_detail_text(record)
        self.detail_text.configure(state="normal")
        self.detail_text.delete("1.0", "end")
        self.detail_text.insert("1.0", text)
        self.detail_text.configure(state="disabled")

    def open_create_dialog(self) -> None:
        self._open_dialog(None)

    def open_edit_dialog(self) -> None:
        if not self.selected_id:
            show_info("Selection", f"Select a {self.singular_title.lower()} first.", parent=self)
            return
        record = self.service.get_record(self.selected_id)
        if not record:
            show_error("Missing", f"Selected {self.singular_title.lower()} was not found.", parent=self)
            return
        self._open_dialog(record)

    def _open_dialog(self, record: dict[str, str] | None) -> None:
        dialog = RecordFormDialog(
            self,
            title=f"{'Edit' if record else 'New'} {self.singular_title}",
            fields=self.build_form_fields(record),
            initial_data=record,
        )
        self.wait_window(dialog)
        if not dialog.result:
            return
        try:
            if record:
                saved = self.service.update_record(record[self.service.id_field], dialog.result, actor_user_id=self.shell.current_user["user_id"])
                self.selected_id = saved[self.service.id_field]
                self.shell.set_status(f"{self.singular_title} updated.")
            else:
                saved = self.service.create_record(dialog.result, actor_user_id=self.shell.current_user["user_id"])
                self.selected_id = saved[self.service.id_field]
                self.shell.set_status(f"{self.singular_title} created.")
            self.reload()
        except ValidationError as error:
            show_error("Validation", str(error), parent=self)
            self.shell.set_status(str(error))

    def delete_selected(self) -> None:
        if not self.selected_id:
            show_info("Selection", f"Select a {self.singular_title.lower()} first.", parent=self)
            return
        if not ask_confirmation("Confirm deletion", f"Delete selected {self.singular_title.lower()}?", parent=self):
            return
        try:
            self.service.delete_record(self.selected_id, actor_user_id=self.shell.current_user["user_id"])
            self.shell.set_status(f"{self.singular_title} deleted.")
            self.selected_id = None
            self.reload()
        except ValidationError as error:
            show_error("Delete blocked", str(error), parent=self)
            self.shell.set_status(str(error))

    def export_rows(self) -> None:
        if not self.current_rows:
            show_info("Export", "Nothing to export for the current filter.", parent=self)
            return
        default_name = f"{self.title.lower().replace(' ', '_')}.csv"
        target = filedialog.asksaveasfilename(
            parent=self,
            initialdir=EXPORT_DIR,
            defaultextension=".csv",
            initialfile=default_name,
            filetypes=[("CSV files", "*.csv")],
        )
        if not target:
            return
        self.service.export_records(Path(target), self.current_rows, actor_user_id=self.shell.current_user["user_id"])
        self.shell.set_status(f"Exported {len(self.current_rows)} {self.title.lower()} records.")
        show_info("Export complete", f"Saved to:\n{target}", parent=self)

    def import_rows(self) -> None:
        source = filedialog.askopenfilename(
            parent=self,
            filetypes=[("CSV files", "*.csv")],
        )
        if not source:
            return
        try:
            created, updated = self.service.import_records(Path(source), actor_user_id=self.shell.current_user["user_id"])
        except (ValidationError, ValueError) as error:
            show_error("Import failed", str(error), parent=self)
            self.shell.set_status(str(error))
            return
        self.reload()
        message = f"Imported {created} new and {updated} updated records."
        self.shell.set_status(message)
        show_info("Import complete", message, parent=self)
