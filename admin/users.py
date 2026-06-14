"""
admin/users.py
User management: view, search, edit, delete, block/activate
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))


import customtkinter as ctk
import tkinter as tk
from config.database import Database
from theme import COLORS, FONTS, make_button, make_entry, make_label, show_message, ask_confirm
from admin.movies import MovieTable


class UsersPanel(ctk.CTkFrame):
    def __init__(self, parent, user=None, **kwargs):
        super().__init__(parent, fg_color=COLORS["bg_dark"], corner_radius=0, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self._users     = []
        self._filtered  = []
        self._build()
        self._load()

    def _build(self):
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 8))
        top.grid_columnconfigure(1, weight=1)

        make_label(top, "User Management", style="heading").grid(row=0, column=0, sticky="w")

        ctrl = ctk.CTkFrame(top, fg_color="transparent")
        ctrl.grid(row=0, column=1, sticky="e")

        self._search_var = tk.StringVar()
        self._search_var.trace_add("write", lambda *_: self._filter())
        make_entry(ctrl, placeholder="Search users…", width=240,
                   textvariable=self._search_var).pack(side="left", padx=(0, 8))

        self._role_var = tk.StringVar(value="All Roles")
        ctk.CTkOptionMenu(ctrl, values=["All Roles", "admin", "user"],
                          variable=self._role_var,
                          fg_color=COLORS["bg_input"], button_color=COLORS["bg_hover"],
                          text_color=COLORS["text_primary"], font=FONTS["body"],
                          command=lambda _: self._filter()).pack(side="left")

        self._table = MovieTable(self, [], [], height=460, on_select=self._on_select)
        self._table.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 8))

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.grid(row=2, column=0, sticky="e", padx=24, pady=(0, 16))
        make_button(btn_row, "✏  Edit",   command=self._edit,   style="ghost").pack(side="left", padx=4)
        make_button(btn_row, "🔒  Block",  command=self._block,  style="ghost").pack(side="left", padx=4)
        make_button(btn_row, "✅  Activate", command=self._activate, style="success").pack(side="left", padx=4)
        make_button(btn_row, "🗑  Delete", command=self._delete, style="danger").pack(side="left", padx=4)

    def _load(self):
        self._users    = list(Database.users().find())
        self._filtered = self._users[:]
        self._refresh()

    def _refresh(self):
        cols = ["Name", "Username", "Email", "Role", "Status"]
        rows = [[u.get("name",""), u.get("username",""), u.get("email",""),
                 u.get("role",""), u.get("status","")] for u in self._filtered]
        self._table.columns = cols
        self._table.update_rows(rows)

    def _filter(self):
        q = self._search_var.get().lower()
        r = self._role_var.get()
        self._filtered = [
            u for u in self._users
            if (q in u.get("name","").lower() or q in u.get("username","").lower()
                or q in u.get("email","").lower())
            and (r == "All Roles" or u.get("role","") == r)
        ]
        self._refresh()

    def _on_select(self, idx):
        self._sel_idx = idx

    def _selected(self):
        idx = self._table.get_selected_index()
        if idx is None:
            show_message(self, "Select", "Please select a user.", "warning")
            return None
        return self._filtered[idx]

    def _edit(self):
        u = self._selected()
        if u:
            UserEditDialog(self, u, on_save=lambda d: self._save_edit(u["_id"], d))

    def _save_edit(self, uid, data):
        Database.users().update_one({"_id": uid}, {"$set": data})
        show_message(self, "Updated", "User updated.", "success")
        self._load()

    def _block(self):
        u = self._selected()
        if u:
            Database.users().update_one({"_id": u["_id"]}, {"$set": {"status": "blocked"}})
            show_message(self, "Blocked", f"User '{u['username']}' blocked.", "warning")
            self._load()

    def _activate(self):
        u = self._selected()
        if u:
            Database.users().update_one({"_id": u["_id"]}, {"$set": {"status": "active"}})
            show_message(self, "Activated", f"User '{u['username']}' activated.", "success")
            self._load()

    def _delete(self):
        u = self._selected()
        if u and ask_confirm(self, "Delete User",
                              f"Delete user '{u.get('username')}'? This cannot be undone."):
            Database.users().delete_one({"_id": u["_id"]})
            show_message(self, "Deleted", "User deleted.", "success")
            self._load()


class UserEditDialog(ctk.CTkToplevel):
    def __init__(self, parent, user, on_save=None):
        super().__init__(parent)
        self.title("Edit User")
        self.geometry("440x360")
        self.configure(fg_color=COLORS["bg_card"])
        self.grab_set()
        self.resizable(False, False)
        self.on_save = on_save

        make_label(self, "Edit User", style="subhead").pack(pady=(20, 16), padx=30, anchor="w")

        self._name_e  = self._field("Full Name",  user.get("name",""))
        self._email_e = self._field("Email",      user.get("email",""))

        make_label(self, "Role", style="small").pack(anchor="w", padx=30, pady=(8, 3))
        self._role = tk.StringVar(value=user.get("role","user"))
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(anchor="w", padx=30)
        for val, lbl in [("user","👤 User"),("admin","🛡 Admin")]:
            ctk.CTkRadioButton(row, text=lbl, variable=self._role, value=val,
                               font=FONTS["body"], text_color=COLORS["text_primary"],
                               fg_color=COLORS["accent"]).pack(side="left", padx=8)

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(pady=20)
        make_button(btn_row, "Save", command=self._save).pack(side="left", padx=6)
        make_button(btn_row, "Cancel", command=self.destroy, style="ghost").pack(side="left", padx=6)

    def _field(self, label, value):
        make_label(self, label, style="small").pack(anchor="w", padx=30, pady=(8, 3))
        e = make_entry(self, placeholder=label, width=380)
        e.pack(padx=30)
        e.insert(0, value)
        return e

    def _save(self):
        data = {"name": self._name_e.get().strip(),
                "email": self._email_e.get().strip(),
                "role":  self._role.get()}
        if self.on_save:
            self.on_save(data)
        self.destroy()
