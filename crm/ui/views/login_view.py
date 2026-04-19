from __future__ import annotations

import customtkinter as ctk


class LoginView(ctk.CTkFrame):
    def __init__(self, master, *, on_login) -> None:
        super().__init__(master, fg_color="transparent")
        self.on_login = on_login
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)

        hero = ctk.CTkFrame(self, corner_radius=0, fg_color=("#E9EEF9", "#0F172A"))
        hero.grid(row=0, column=0, sticky="nsew")
        hero.grid_columnconfigure(0, weight=1)
        hero.grid_rowconfigure(0, weight=1)

        hero_content = ctk.CTkFrame(hero, fg_color="transparent")
        hero_content.grid(row=0, column=0, sticky="nsew", padx=48, pady=48)
        hero_content.grid_columnconfigure(0, weight=1)

        badge = ctk.CTkLabel(
            hero_content,
            text="OFFLINE DESKTOP CRM",
            text_color=("#2F7BFF", "#6EA4FF"),
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        badge.grid(row=0, column=0, sticky="w", pady=(0, 24))
        title = ctk.CTkLabel(
            hero_content,
            text="EstateFlow CRM",
            font=ctk.CTkFont(size=36, weight="bold"),
            anchor="w",
        )
        title.grid(row=1, column=0, sticky="w")
        description = ctk.CTkLabel(
            hero_content,
            text="Daily real-estate operations in one local desktop workspace: leads, listings, pipeline, appointments, tasks, notes, and reporting.",
            justify="left",
            wraplength=520,
            text_color=("#40506E", "#B6C2E0"),
            font=ctk.CTkFont(size=16),
            anchor="w",
        )
        description.grid(row=2, column=0, sticky="w", pady=(16, 32))

        bullet_text = [
            "Role-based local access",
            "Atomic CSV persistence with audit log",
            "Dashboard, reports, exports, and backups",
        ]
        for index, item in enumerate(bullet_text, start=3):
            bullet = ctk.CTkLabel(hero_content, text=f"• {item}", anchor="w", font=ctk.CTkFont(size=15))
            bullet.grid(row=index, column=0, sticky="w", pady=6)

        panel = ctk.CTkFrame(self, corner_radius=0)
        panel.grid(row=0, column=1, sticky="nsew")
        panel.grid_rowconfigure(0, weight=1)
        panel.grid_columnconfigure(0, weight=1)

        card = ctk.CTkFrame(panel, width=420, height=420, corner_radius=24, fg_color=("white", "#1B2437"))
        card.grid(row=0, column=0, sticky="", padx=40, pady=40)
        card.grid_columnconfigure(0, weight=1)

        heading = ctk.CTkLabel(card, text="Sign In", font=ctk.CTkFont(size=28, weight="bold"))
        heading.grid(row=0, column=0, sticky="w", padx=28, pady=(28, 8))
        hint = ctk.CTkLabel(
            card,
            text="Default admin: admin / Admin123!",
            text_color=("#65748B", "#9AA8C8"),
            anchor="w",
        )
        hint.grid(row=1, column=0, sticky="w", padx=28, pady=(0, 24))

        self.username_entry = ctk.CTkEntry(card, placeholder_text="Username")
        self.username_entry.grid(row=2, column=0, sticky="ew", padx=28, pady=(0, 14))
        self.password_entry = ctk.CTkEntry(card, placeholder_text="Password", show="*")
        self.password_entry.grid(row=3, column=0, sticky="ew", padx=28, pady=(0, 14))
        self.feedback_label = ctk.CTkLabel(card, text="", text_color="#E85B5B", anchor="w")
        self.feedback_label.grid(row=4, column=0, sticky="w", padx=28, pady=(0, 10))
        login_button = ctk.CTkButton(card, text="Log In", height=42, command=self._submit)
        login_button.grid(row=5, column=0, sticky="ew", padx=28, pady=(10, 28))

        self.username_entry.insert(0, "admin")
        self.password_entry.bind("<Return>", lambda _event: self._submit())
        self.username_entry.focus_set()

    def set_error(self, message: str) -> None:
        self.feedback_label.configure(text=message)

    def _submit(self) -> None:
        self.feedback_label.configure(text="")
        self.on_login(self.username_entry.get().strip(), self.password_entry.get().strip())
