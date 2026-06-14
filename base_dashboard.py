"""
base_dashboard.py  –  Shared sidebar + content-frame scaffold
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))


import customtkinter as ctk
import tkinter as tk
from theme import COLORS, FONTS, make_label


class BaseDashboard(ctk.CTk):
    """
    Provides a sidebar + right-side content frame.
    Subclass must define:
        MENU_ITEMS  – list of (icon, label, handler_method_name)
        WINDOW_TITLE
        WINDOW_SIZE
    """
    MENU_ITEMS = []
    WINDOW_TITLE = "Dashboard"
    WINDOW_SIZE = "1280x760"

    def __init__(self, user):
        super().__init__()
        self.user = user
        self.title(self.WINDOW_TITLE)
        self.geometry(self.WINDOW_SIZE)
        self.minsize(1100, 680)
        self.configure(fg_color=COLORS["bg_dark"])
        self._active_btn = None
        self._build_scaffold()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ─── Scaffold ─────────────────────────────────────────────────────────────
    def _build_scaffold(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0,
                                    fg_color=COLORS["bg_sidebar"])
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        self._build_sidebar()

        # Content
        self.content = ctk.CTkFrame(self, corner_radius=0, fg_color=COLORS["bg_dark"])
        self.content.grid(row=0, column=1, sticky="nsew", padx=0)
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

    def _build_sidebar(self):
        # Logo
        logo = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo.pack(pady=(24, 8), padx=16)
        ctk.CTkLabel(logo, text="🎬  CineVault", font=("Georgia", 17, "bold"),
                     text_color=COLORS["accent"]).pack(anchor="w")
        make_label(logo, self._role_tag(), style="small").pack(anchor="w")

        ctk.CTkFrame(self.sidebar, height=1, fg_color=COLORS["text_muted"],
                     corner_radius=0).pack(fill="x", padx=16, pady=(8, 16))

        # Menu items
        self._menu_buttons = {}
        for icon, label, method in self.MENU_ITEMS:
            btn = self._sidebar_btn(icon, label, method)
            self._menu_buttons[label] = btn

        # Spacer
        ctk.CTkFrame(self.sidebar, fg_color="transparent").pack(fill="y", expand=True)

        # User info at bottom
        ctk.CTkFrame(self.sidebar, height=1, fg_color=COLORS["text_muted"],
                     corner_radius=0).pack(fill="x", padx=16, pady=(0, 12))
        info = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        info.pack(padx=16, pady=(0, 12))
        ctk.CTkLabel(info, text=self.user.get("name", "User"),
                     font=FONTS["body"], text_color=COLORS["text_primary"],
                     anchor="w").pack(anchor="w")
        ctk.CTkLabel(info, text=self.user.get("username", ""),
                     font=FONTS["small"], text_color=COLORS["text_muted"],
                     anchor="w").pack(anchor="w")

    def _sidebar_btn(self, icon, label, method):
        def click():
            self._set_active(label)
            getattr(self, method)()

        btn = ctk.CTkButton(
            self.sidebar,
            text=f"  {icon}  {label}",
            font=FONTS["sidebar"],
            text_color=COLORS["sidebar_text"],
            fg_color="transparent",
            hover_color=COLORS["sidebar_active"],
            anchor="w",
            height=40,
            corner_radius=8,
            command=click,
        )
        btn.pack(fill="x", padx=10, pady=2)
        return btn

    def _set_active(self, label):
        for lbl, btn in self._menu_buttons.items():
            if lbl == label:
                btn.configure(fg_color=COLORS["sidebar_active"],
                              text_color=COLORS["accent"])
            else:
                btn.configure(fg_color="transparent",
                              text_color=COLORS["sidebar_text"])

    def _role_tag(self):
        role = self.user.get("role", "user")
        return "Administrator" if role == "admin" else "User Account"

    # ─── Content Area Helpers ─────────────────────────────────────────────────
    def clear_content(self):
        for w in self.content.winfo_children():
            w.destroy()

    def _on_close(self):
        from config.database import Database
        Database.close()
        self.destroy()
