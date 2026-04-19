from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable

import customtkinter as ctk


class TableWidget(ctk.CTkFrame):
    def __init__(self, master, *, columns: list[tuple[str, str, int]], on_sort: Callable[[str], None] | None = None) -> None:
        super().__init__(master, fg_color="transparent")
        self.columns = columns
        self.on_sort = on_sort
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(
            self,
            columns=[column[0] for column in columns],
            show="headings",
            selectmode="browse",
        )
        for key, title, width in columns:
            self.tree.heading(key, text=title, command=lambda field=key: self._handle_sort(field))
            self.tree.column(key, width=width, anchor=tk.W, stretch=True)
        self.tree.grid(row=0, column=0, sticky="nsew")

        self.vertical_scroll = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.vertical_scroll.grid(row=0, column=1, sticky="ns")
        self.horizontal_scroll = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        self.horizontal_scroll.grid(row=1, column=0, sticky="ew")
        self.tree.configure(yscrollcommand=self.vertical_scroll.set, xscrollcommand=self.horizontal_scroll.set)

    def _handle_sort(self, field: str) -> None:
        if self.on_sort:
            self.on_sort(field)

    def clear(self) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)

    def load_rows(self, rows: list[dict[str, str]], *, row_id_field: str) -> None:
        self.clear()
        for row in rows:
            values = [row.get(column[0], "") for column in self.columns]
            item_id = row.get(row_id_field) or f"row-{len(self.tree.get_children())}"
            self.tree.insert("", "end", iid=item_id, values=values)

    def bind_select(self, callback: Callable[[], None]) -> None:
        self.tree.bind("<<TreeviewSelect>>", lambda _event: callback())

    def selected_id(self) -> str | None:
        selection = self.tree.selection()
        return selection[0] if selection else None
