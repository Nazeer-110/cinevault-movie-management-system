"""
authentication/forgot_password.py
Simple forgot password via username + email reset
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))


import customtkinter as ctk
import bcrypt
from config.database import Database
from theme import COLORS, FONTS, make_button, make_entry, make_label, show_message


class ForgotPasswordWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Reset Password")
        self.geometry("440x360")
        self.configure(fg_color=COLORS["bg_card"])
        self.grab_set()
        self.resizable(False, False)

        # Center
        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() - 440) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - 360) // 2
        self.geometry(f"+{x}+{y}")

        make_label(self, "Reset Password", style="heading").pack(pady=(24, 4))
        make_label(self, "Enter your username and new password", style="small").pack(pady=(0, 20))

        make_label(self, "Username", style="small").pack(anchor="w", padx=40)
        self._username = make_entry(self, placeholder="Your username", width=360)
        self._username.pack(padx=40, pady=(4, 12))

        make_label(self, "New Password", style="small").pack(anchor="w", padx=40)
        self._pw = make_entry(self, placeholder="New password", show="●", width=360)
        self._pw.pack(padx=40, pady=(4, 12))

        make_label(self, "Confirm Password", style="small").pack(anchor="w", padx=40)
        self._cpw = make_entry(self, placeholder="Confirm password", show="●", width=360)
        self._cpw.pack(padx=40, pady=(4, 20))

        make_button(self, "Reset Password", command=self._reset, width=360).pack(padx=40)

    def _reset(self):
        username = self._username.get().strip()
        pw = self._pw.get()
        cpw = self._cpw.get()

        if not all([username, pw, cpw]):
            show_message(self, "Error", "All fields required.", "error"); return
        if pw != cpw:
            show_message(self, "Error", "Passwords do not match.", "error"); return
        if len(pw) < 6:
            show_message(self, "Error", "Password must be ≥ 6 characters.", "error"); return

        user = Database.users().find_one({"username": username})
        if not user:
            show_message(self, "Error", "Username not found.", "error"); return

        hashed = bcrypt.hashpw(pw.encode(), bcrypt.gensalt())
        Database.users().update_one({"username": username}, {"$set": {"password": hashed}})
        show_message(self, "Success", "Password reset successfully!", "success")
        self.after(1200, self.destroy)
