from __future__ import annotations

import tkinter as tk
from tkinter import ttk

import customtkinter as ctk

from crm.config import DEFAULT_APPEARANCE_MODE, DEFAULT_COLOR_THEME


def initialize_theme() -> None:
    ctk.set_appearance_mode(DEFAULT_APPEARANCE_MODE)
    ctk.set_default_color_theme(DEFAULT_COLOR_THEME)


def apply_ttk_theme(root: tk.Misc, mode: str | None = None) -> None:
    active_mode = (mode or ctk.get_appearance_mode()).lower()
    is_dark = active_mode == "dark"
    background = "#151B2D" if is_dark else "#F4F6FB"
    surface = "#1E2740" if is_dark else "#FFFFFF"
    foreground = "#F2F5FF" if is_dark else "#1B2437"
    muted = "#7B86A8" if is_dark else "#6C7896"
    selection = "#2F7BFF"

    style = ttk.Style(root)
    style.theme_use("default")
    style.configure(
        "Treeview",
        background=surface,
        fieldbackground=surface,
        foreground=foreground,
        borderwidth=0,
        rowheight=28,
    )
    style.map("Treeview", background=[("selected", selection)], foreground=[("selected", "#FFFFFF")])
    style.configure(
        "Treeview.Heading",
        background=background,
        foreground=muted,
        relief="flat",
        borderwidth=0,
        padding=(8, 10),
    )
    style.map("Treeview.Heading", background=[("active", background)])
    style.configure(
        "Vertical.TScrollbar",
        gripcount=0,
        background=surface,
        troughcolor=background,
        arrowcolor=foreground,
        borderwidth=0,
    )
    style.configure(
        "Horizontal.TScrollbar",
        gripcount=0,
        background=surface,
        troughcolor=background,
        arrowcolor=foreground,
        borderwidth=0,
    )
