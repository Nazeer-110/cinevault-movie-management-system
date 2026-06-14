"""
user/profile.py
User profile: view/update info and change password
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))


import customtkinter as ctk
import bcrypt
from config.database import Database
from theme import COLORS, FONTS, make_button, make_entry, make_label, make_card, show_message


class ProfilePanel(ctk.CTkFrame):
    def __init__(self, parent, user, **kwargs):
        super().__init__(parent, fg_color=COLORS["bg_dark"], corner_radius=0, **kwargs)
        self.user = user
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._build()

    def _build(self):
        scroll = ctk.CTkScrollableFrame(self, fg_color=COLORS["bg_dark"],
                                        scrollbar_button_color=COLORS["bg_card"])
        scroll.grid(row=0, column=0, sticky="nsew", padx=24, pady=20)
        scroll.grid_columnconfigure((0, 1), weight=1)

        make_label(scroll, "My Profile", style="heading").grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 20))

        # Profile info card
        info_card = make_card(scroll)
        info_card.grid(row=1, column=0, padx=8, pady=8, sticky="nsew")

        ctk.CTkLabel(info_card, text="👤", font=("Segoe UI Emoji", 48)).pack(pady=(24, 8))
        ctk.CTkLabel(info_card, text=self.user.get("name",""),
                     font=("Georgia", 18, "bold"), text_color=COLORS["text_primary"]).pack()
        ctk.CTkLabel(info_card, text=f"@{self.user.get('username','')}",
                     font=FONTS["body"], text_color=COLORS["accent"]).pack(pady=4)
        ctk.CTkLabel(info_card, text=self.user.get("email",""),
                     font=FONTS["small"], text_color=COLORS["text_secondary"]).pack()
        ctk.CTkLabel(info_card, text=self.user.get("role","user").capitalize(),
                     font=FONTS["small"], text_color=COLORS["text_muted"]).pack(pady=(4, 0))

        # Stats
        ctk.CTkFrame(info_card, height=1, fg_color=COLORS["text_muted"]).pack(fill="x", padx=20, pady=16)
        stats = ctk.CTkFrame(info_card, fg_color="transparent")
        stats.pack(padx=20, pady=(0, 20))
        favs    = Database.favorites().count_documents({"user_id": self.user["_id"]})
        reviews = Database.reviews().count_documents({"user_id": self.user["_id"]})
        for icon, lbl, val in [("❤", "Favorites", favs), ("⭐", "Reviews", reviews)]:
            col = ctk.CTkFrame(stats, fg_color=COLORS["bg_input"], corner_radius=8, width=100)
            col.pack(side="left", padx=6)
            col.pack_propagate(False)
            ctk.CTkLabel(col, text=icon, font=("Segoe UI Emoji", 20)).pack(pady=(10, 2))
            ctk.CTkLabel(col, text=str(val), font=("Georgia", 18, "bold"),
                         text_color=COLORS["accent"]).pack()
            ctk.CTkLabel(col, text=lbl, font=FONTS["small"],
                         text_color=COLORS["text_muted"]).pack(pady=(0, 10))

        # Edit profile card
        edit_card = make_card(scroll)
        edit_card.grid(row=1, column=1, padx=8, pady=8, sticky="nsew")

        make_label(edit_card, "Edit Profile", style="subhead").pack(
            anchor="w", padx=20, pady=(20, 12))

        self._name_e  = self._field(edit_card, "Full Name",  self.user.get("name",""))
        self._email_e = self._field(edit_card, "Email",      self.user.get("email",""))

        make_button(edit_card, "Save Changes", command=self._update, width=220).pack(pady=12)

        ctk.CTkFrame(edit_card, height=1, fg_color=COLORS["text_muted"]).pack(
            fill="x", padx=20, pady=(0, 12))
        make_label(edit_card, "Change Password", style="subhead").pack(anchor="w", padx=20, pady=(0,8))

        self._old_pw = self._field(edit_card, "Current Password", "", pw=True)
        self._new_pw = self._field(edit_card, "New Password",     "", pw=True)
        self._cfm_pw = self._field(edit_card, "Confirm Password", "", pw=True)

        make_button(edit_card, "Update Password", command=self._change_pw,
                    style="ghost", width=220).pack(pady=(8, 20))

    def _field(self, parent, label, value, pw=False):
        make_label(parent, label, style="small").pack(anchor="w", padx=20, pady=(4,2))
        e = make_entry(parent, placeholder=label, show="●" if pw else None, width=240)
        e.pack(padx=20)
        if value:
            e.insert(0, value)
        return e

    def _update(self):
        name  = self._name_e.get().strip()
        email = self._email_e.get().strip()
        if not name or not email:
            show_message(self, "Error", "Name and email required.", "error"); return
        import re
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            show_message(self, "Error", "Invalid email.", "error"); return

        Database.users().update_one({"_id": self.user["_id"]},
                                    {"$set": {"name": name, "email": email}})
        self.user["name"]  = name
        self.user["email"] = email
        show_message(self, "Saved", "Profile updated!", "success")

    def _change_pw(self):
        old = self._old_pw.get()
        new = self._new_pw.get()
        cfm = self._cfm_pw.get()
        if not all([old, new, cfm]):
            show_message(self, "Error", "All password fields required.", "error"); return
        if not bcrypt.checkpw(old.encode(), self.user["password"]):
            show_message(self, "Error", "Current password is incorrect.", "error"); return
        if new != cfm:
            show_message(self, "Error", "New passwords do not match.", "error"); return
        if len(new) < 6:
            show_message(self, "Error", "New password must be ≥ 6 characters.", "error"); return
        hashed = bcrypt.hashpw(new.encode(), bcrypt.gensalt())
        Database.users().update_one({"_id": self.user["_id"]},
                                    {"$set": {"password": hashed}})
        self.user["password"] = hashed
        show_message(self, "Success", "Password changed successfully!", "success")
        self._old_pw.delete(0, "end")
        self._new_pw.delete(0, "end")
        self._cfm_pw.delete(0, "end")
