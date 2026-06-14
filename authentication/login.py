"""
authentication/login.py
Modern login form with show/hide password and remember-me
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))


import customtkinter as ctk
import tkinter as tk
import bcrypt
import json
import os
from config.database import Database
from theme import COLORS, FONTS, make_button, make_entry, make_label, show_message

REMEMBER_FILE = os.path.join(os.path.dirname(__file__), "..", "assets", "remember.json")


class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("CineVault – Login")
        self.geometry("900x580")
        self.resizable(False, False)
        self.configure(fg_color=COLORS["bg_dark"])
        self._build_ui()
        self._load_remembered()

    # ─── Build UI ─────────────────────────────────────────────────────────────
    def _build_ui(self):
        # Left decorative panel
        left = ctk.CTkFrame(self, width=420, fg_color=COLORS["bg_sidebar"], corner_radius=0)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        ctk.CTkLabel(left, text="🎬", font=("Segoe UI Emoji", 52)).pack(pady=(80, 8))
        ctk.CTkLabel(left, text="CineVault", font=("Georgia", 32, "bold"),
                     text_color=COLORS["accent"]).pack()
        ctk.CTkLabel(left, text="Movie Management System",
                     font=FONTS["body"], text_color=COLORS["text_secondary"]).pack(pady=(4, 40))

        for tip in ["📽  Manage your entire movie catalog",
                    "⭐  Track ratings & reviews",
                    "👥  Admin & User role system",
                    "📊  Generate detailed reports"]:
            row = ctk.CTkFrame(left, fg_color="transparent")
            row.pack(anchor="w", padx=40, pady=4)
            ctk.CTkLabel(row, text=tip, font=FONTS["body"],
                         text_color=COLORS["text_secondary"]).pack(anchor="w")

        # Right login panel
        right = ctk.CTkFrame(self, fg_color=COLORS["bg_dark"], corner_radius=0)
        right.pack(side="left", fill="both", expand=True)

        form = ctk.CTkFrame(right, fg_color="transparent")
        form.place(relx=0.5, rely=0.5, anchor="center")

        make_label(form, "Welcome Back", style="heading").pack(anchor="w", pady=(0, 4))
        make_label(form, "Sign in to your account", style="small").pack(anchor="w", pady=(0, 28))

        # Username
        make_label(form, "Username", style="small").pack(anchor="w")
        self.username_entry = make_entry(form, placeholder="Enter username", width=320)
        self.username_entry.pack(pady=(4, 14))

        # Password
        make_label(form, "Password", style="small").pack(anchor="w")
        pw_row = ctk.CTkFrame(form, fg_color="transparent")
        pw_row.pack(pady=(4, 6))
        self.password_entry = make_entry(pw_row, placeholder="Enter password", show="●", width=278)
        self.password_entry.pack(side="left")
        self.show_pw = False
        self.eye_btn = ctk.CTkButton(pw_row, text="👁", width=36, height=38,
                                     fg_color=COLORS["bg_input"],
                                     hover_color=COLORS["bg_hover"],
                                     text_color=COLORS["text_secondary"],
                                     corner_radius=8,
                                     command=self._toggle_pw)
        self.eye_btn.pack(side="left", padx=(4, 0))

        # Options row
        opt_row = ctk.CTkFrame(form, fg_color="transparent")
        opt_row.pack(fill="x", pady=(4, 20))
        self.remember_var = tk.BooleanVar()
        ctk.CTkCheckBox(opt_row, text="Remember Me", variable=self.remember_var,
                        font=FONTS["small"], text_color=COLORS["text_secondary"],
                        fg_color=COLORS["accent"], hover_color=COLORS["accent_dark"],
                        checkmark_color="#000000").pack(side="left")
        ctk.CTkButton(opt_row, text="Forgot Password?", font=FONTS["small"],
                      text_color=COLORS["accent"], fg_color="transparent",
                      hover_color="transparent", command=self._forgot_password).pack(side="right")

        make_button(form, "Sign In", command=self._login, width=320, height=42).pack(pady=(0, 16))

        # Register link
        reg_row = ctk.CTkFrame(form, fg_color="transparent")
        reg_row.pack()
        make_label(reg_row, "Don't have an account?", style="small").pack(side="left", padx=(0, 4))
        ctk.CTkButton(reg_row, text="Register", font=FONTS["small"],
                      text_color=COLORS["accent"], fg_color="transparent",
                      hover_color="transparent", command=self._open_register).pack(side="left")

        # Enter key
        self.bind("<Return>", lambda e: self._login())

    # ─── Actions ──────────────────────────────────────────────────────────────
    def _toggle_pw(self):
        self.show_pw = not self.show_pw
        self.password_entry.configure(show="" if self.show_pw else "●")

    def _login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            show_message(self, "Validation Error", "Please fill in all fields.", "error")
            return

        user = Database.users().find_one({"username": username})
        if not user:
            show_message(self, "Login Failed", "Username not found.", "error")
            return

        if user.get("status") == "blocked":
            show_message(self, "Account Blocked",
                         "Your account has been blocked. Contact admin.", "error")
            return

        if not bcrypt.checkpw(password.encode(), user["password"]):
            show_message(self, "Login Failed", "Incorrect password.", "error")
            return

        if self.remember_var.get():
            self._save_remember(username)
        else:
            self._clear_remember()

        role = user.get("role", "user")
        self._launch_dashboard(user, role)

    def _launch_dashboard(self, user, role):
        self.destroy()
        if role == "admin":
            from admin.dashboard import AdminDashboard
            app = AdminDashboard(user)
        else:
            from user.dashboard import UserDashboard
            app = UserDashboard(user)
        app.mainloop()

    def _forgot_password(self):
        from authentication.forgot_password import ForgotPasswordWindow
        ForgotPasswordWindow(self)

    def _open_register(self):
        from authentication.register import RegisterWindow
        self.destroy()
        RegisterWindow().mainloop()

    def _save_remember(self, username):
        os.makedirs(os.path.dirname(REMEMBER_FILE), exist_ok=True)
        with open(REMEMBER_FILE, "w") as f:
            json.dump({"username": username}, f)

    def _clear_remember(self):
        if os.path.exists(REMEMBER_FILE):
            os.remove(REMEMBER_FILE)

    def _load_remembered(self):
        if os.path.exists(REMEMBER_FILE):
            try:
                with open(REMEMBER_FILE) as f:
                    data = json.load(f)
                    self.username_entry.insert(0, data.get("username", ""))
                    self.remember_var.set(True)
            except Exception:
                pass
