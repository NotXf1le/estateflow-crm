from __future__ import annotations

from dataclasses import dataclass, field
from tkinter import messagebox

import customtkinter as ctk


@dataclass
class FieldSpec:
    key: str
    label: str
    widget_type: str = "entry"
    options: list[tuple[str, str]] = field(default_factory=list)
    required: bool = False
    placeholder: str = ""
    height: int = 96


class RecordFormDialog(ctk.CTkToplevel):
    def __init__(
        self,
        master,
        *,
        title: str,
        fields: list[FieldSpec],
        initial_data: dict[str, str] | None = None,
    ) -> None:
        super().__init__(master)
        self.title(title)
        self.fields = fields
        self.initial_data = initial_data or {}
        self.result: dict[str, str] | None = None
        self.widgets: dict[str, ctk.CTkBaseClass] = {}
        self.option_maps: dict[str, dict[str, str]] = {}
        self.transient(master)
        self.grab_set()
        self.geometry("640x720")
        self.minsize(520, 520)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        container.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        container.grid_columnconfigure(1, weight=1)

        for row_index, spec in enumerate(fields):
            label = ctk.CTkLabel(container, text=spec.label, anchor="w")
            label.grid(row=row_index, column=0, sticky="w", padx=(0, 12), pady=(0, 14))
            widget = self._build_widget(container, spec)
            widget.grid(row=row_index, column=1, sticky="ew", pady=(0, 14))
            self.widgets[spec.key] = widget

        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 20))
        footer.grid_columnconfigure(0, weight=1)
        cancel_button = ctk.CTkButton(footer, text="Cancel", fg_color="transparent", border_width=1, command=self.destroy)
        cancel_button.grid(row=0, column=1, padx=(0, 8))
        save_button = ctk.CTkButton(footer, text="Save", command=self._save)
        save_button.grid(row=0, column=2)

    def _build_widget(self, master, spec: FieldSpec):
        current_value = self.initial_data.get(spec.key, "")
        if spec.widget_type == "textbox":
            widget = ctk.CTkTextbox(master, height=spec.height)
            widget.insert("1.0", current_value)
            return widget
        if spec.widget_type == "combo":
            labels = [label for _, label in spec.options] or [""]
            mapping = {label: value for value, label in spec.options}
            reverse_mapping = {value: label for value, label in spec.options}
            self.option_maps[spec.key] = mapping
            widget = ctk.CTkComboBox(master, values=labels, state="readonly")
            widget.set(reverse_mapping.get(current_value, labels[0]))
            return widget
        kwargs = {"placeholder_text": spec.placeholder}
        if spec.widget_type == "password":
            kwargs["show"] = "*"
        widget = ctk.CTkEntry(master, **kwargs)
        widget.insert(0, current_value)
        return widget

    def _read_widget_value(self, spec: FieldSpec) -> str:
        widget = self.widgets[spec.key]
        if spec.widget_type == "textbox":
            return widget.get("1.0", "end").strip()
        if spec.widget_type == "combo":
            label = widget.get().strip()
            return self.option_maps[spec.key].get(label, "")
        return widget.get().strip()

    def _save(self) -> None:
        values: dict[str, str] = {}
        for spec in self.fields:
            value = self._read_widget_value(spec)
            if spec.required and not value:
                messagebox.showerror("Validation", f"{spec.label} is required.", parent=self)
                return
            values[spec.key] = value
        self.result = values
        self.destroy()


def ask_confirmation(title: str, message: str, *, parent=None) -> bool:
    return messagebox.askyesno(title, message, parent=parent)


def show_error(title: str, message: str, *, parent=None) -> None:
    messagebox.showerror(title, message, parent=parent)


def show_info(title: str, message: str, *, parent=None) -> None:
    messagebox.showinfo(title, message, parent=parent)
