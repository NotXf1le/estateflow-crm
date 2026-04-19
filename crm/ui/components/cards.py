from __future__ import annotations

import customtkinter as ctk


class KpiCard(ctk.CTkFrame):
    def __init__(self, master, *, title: str, value: str, accent: str = "#2F7BFF", **kwargs) -> None:
        super().__init__(master, corner_radius=14, fg_color=("white", "#1E2740"), **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.title_label = ctk.CTkLabel(
            self,
            text=title,
            text_color=("#5D6B89", "#9BA8C7"),
            font=ctk.CTkFont(size=13),
            anchor="w",
        )
        self.title_label.grid(row=0, column=0, sticky="ew", padx=18, pady=(16, 4))
        self.value_label = ctk.CTkLabel(
            self,
            text=value,
            font=ctk.CTkFont(size=28, weight="bold"),
            anchor="w",
        )
        self.value_label.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 6))
        self.accent_bar = ctk.CTkFrame(self, height=4, corner_radius=8, fg_color=accent)
        self.accent_bar.grid(row=2, column=0, sticky="ew", padx=18, pady=(0, 16))

    def update_value(self, value: str) -> None:
        self.value_label.configure(text=value)
