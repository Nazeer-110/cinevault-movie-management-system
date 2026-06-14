"""
authentication/register.py
Full registration form with validation
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))


import customtkinter as ctk
import tkinter as tk
import bcrypt
import re
from config.database import Database
from theme import COLORS, FONTS, make_button, make_entry, make_label, show_message


class RegisterWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("CineVault – Register")
        self.geometry("960x660")
        self.resizable(False, False)
        self.configure(fg_color=COLORS["bg_dark"])
        self._build_ui()

    def _build_ui(self):
        # Left panel
        left = ctk.CTkFrame(self, width=340, fg_color=COLORS["bg_sidebar"], corner_radius=0)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        ctk.CTkLabel(left, text="🎬", font=("Segoe UI Emoji", 48)).pack(pady=(80, 8))
        ctk.CTkLabel(left, text="CineVault", font=("Georgia", 28, "bold"),
                     text_color=COLORS["accent"]).pack()
        ctk.CTkLabel(left, text="Join the community",
                     font=FONTS["body"], text_color=COLORS["text_secondary"]).pack(pady=(4, 0))

        # Right form
        right = ctk.CTkScrollableFrame(self, fg_color=COLORS["bg_dark"],
                                       scrollbar_button_color=COLORS["bg_card"],
                                       scrollbar_fg_color=COLORS["bg_dark"])
        right.pack(side="left", fill="both", expand=True, padx=40, pady=20)

        make_label(right, "Create Account", style="heading").pack(anchor="w", pady=(20, 4))
        make_label(right, "Fill in the details below", style="small").pack(anchor="w", pady=(0, 20))

        # Form fields
        self._field(right, "Full Name", "_name_entry", "Enter your full name")
        self._field(right, "Username", "_username_entry", "Choose a username")
        self._field(right, "Email Address", "_email_entry", "your@email.com")
        self._field(right, "Password", "_password_entry", "Min 6 characters", pw=True)
        self._field(right, "Confirm Password", "_confirm_entry", "Repeat password", pw=True)

        # Role selector
        make_label(right, "Role", style="small").pack(anchor="w", pady=(8, 4))
        self._role_var = tk.StringVar(value="user")
        role_row = ctk.CTkFrame(right, fg_color="transparent")
        role_row.pack(anchor="w", pady=(0, 16))
        for val, label in [("user", "👤  User"), ("admin", "🛡  Admin")]:
            ctk.CTkRadioButton(role_row, text=label, variable=self._role_var, value=val,
                               font=FONTS["body"], text_color=COLORS["text_primary"],
                               fg_color=COLORS["accent"],
                               hover_color=COLORS["accent_dark"]).pack(side="left", padx=12)

        make_button(right, "Create Account", command=self._register,
                    width=320, height=42).pack(pady=(8, 12))

        login_row = ctk.CTkFrame(right, fg_color="transparent")
        login_row.pack()
        make_label(login_row, "Already have an account?", style="small").pack(side="left", padx=(0, 4))
        ctk.CTkButton(login_row, text="Sign In", font=FONTS["small"],
                      text_color=COLORS["accent"], fg_color="transparent",
                      hover_color="transparent", command=self._goto_login).pack(side="left")

    def _field(self, parent, label, attr, placeholder, pw=False):
        make_label(parent, label, style="small").pack(anchor="w", pady=(8, 4))
        entry = make_entry(parent, placeholder=placeholder,
                           show="●" if pw else None, width=320)
        entry.pack(pady=(0, 0))
        setattr(self, attr, entry)

    def _register(self):
        name     = self._name_entry.get().strip()
        username = self._username_entry.get().strip()
        email    = self._email_entry.get().strip()
        password = self._password_entry.get()
        confirm  = self._confirm_entry.get()
        role     = self._role_var.get()

        # Validation
        if not all([name, username, email, password, confirm]):
            show_message(self, "Validation", "All fields are required.", "error"); return
        if len(username) < 3:
            show_message(self, "Validation", "Username must be ≥ 3 characters.", "error"); return
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            show_message(self, "Validation", "Enter a valid email address.", "error"); return
        if len(password) < 6:
            show_message(self, "Validation", "Password must be ≥ 6 characters.", "error"); return
        if password != confirm:
            show_message(self, "Validation", "Passwords do not match.", "error"); return

        # Uniqueness
        if Database.users().find_one({"username": username}):
            show_message(self, "Taken", "Username already exists.", "error"); return
        if Database.users().find_one({"email": email}):
            show_message(self, "Taken", "Email already registered.", "error"); return

        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        Database.users().insert_one({
            "name":     name,
            "username": username,
            "email":    email,
            "password": hashed,
            "role":     role,
            "status":   "active",
            "profile_picture": ""
        })
        show_message(self, "Success", "Account created! You can now sign in.", "success")
        self.after(1200, self._goto_login)

    def _goto_login(self):
        from authentication.login import LoginWindow
        self.destroy()
        LoginWindow().mainloop()
