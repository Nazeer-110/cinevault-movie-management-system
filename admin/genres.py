"""
admin/genres.py
Genre CRUD
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))


import customtkinter as ctk
import tkinter as tk
from config.database import Database
from theme import COLORS, FONTS, make_button, make_entry, make_label, show_message, ask_confirm
from admin.movies import MovieTable


class GenresPanel(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color=COLORS["bg_dark"], corner_radius=0, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self._genres   = []
        self._build()
        self._load()

    def _build(self):
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 8))
        top.grid_columnconfigure(1, weight=1)
        make_label(top, "Genre Management", style="heading").grid(row=0, column=0, sticky="w")
        make_button(top, "+ Add Genre", command=self._add).grid(row=0, column=1, sticky="e")

        self._table = MovieTable(self, [], [], height=440, on_select=lambda _: None)
        self._table.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 8))

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.grid(row=2, column=0, sticky="e", padx=24, pady=(0, 16))
        make_button(btn_row, "✏  Edit",   command=self._edit,   style="ghost").pack(side="left", padx=4)
        make_button(btn_row, "🗑  Delete", command=self._delete, style="danger").pack(side="left", padx=4)

    def _load(self):
        self._genres = list(Database.genres().find())
        cols  = ["Genre Name", "Description"]
        rows  = [[g.get("name",""), g.get("description","")] for g in self._genres]
        self._table.columns = cols
        self._table.update_rows(rows)

    def _add(self):
        GenreDialog(self, on_save=lambda d: self._save_new(d))

    def _save_new(self, data):
        Database.genres().insert_one(data)
        show_message(self, "Added", "Genre added!", "success")
        self._load()

    def _edit(self):
        idx = self._table.get_selected_index()
        if idx is None:
            show_message(self, "Select", "Select a genre.", "warning"); return
        g = self._genres[idx]
        GenreDialog(self, genre=g, on_save=lambda d: self._save_edit(g["_id"], d))

    def _save_edit(self, gid, data):
        Database.genres().update_one({"_id": gid}, {"$set": data})
        show_message(self, "Updated", "Genre updated.", "success")
        self._load()

    def _delete(self):
        idx = self._table.get_selected_index()
        if idx is None:
            show_message(self, "Select", "Select a genre.", "warning"); return
        g = self._genres[idx]
        if ask_confirm(self, "Delete", f"Delete genre '{g.get('name')}'?"):
            Database.genres().delete_one({"_id": g["_id"]})
            self._load()


class GenreDialog(ctk.CTkToplevel):
    def __init__(self, parent, genre=None, on_save=None):
        super().__init__(parent)
        self.title("Genre")
        self.geometry("420x260")
        self.configure(fg_color=COLORS["bg_card"])
        self.grab_set()
        self.resizable(False, False)
        self.on_save = on_save

        make_label(self, "Genre Details", style="subhead").pack(pady=(20, 16), padx=30, anchor="w")

        make_label(self, "Name", style="small").pack(anchor="w", padx=30)
        self._name = make_entry(self, placeholder="Genre name", width=360)
        self._name.pack(padx=30, pady=(4, 12))
        if genre:
            self._name.insert(0, genre.get("name",""))

        make_label(self, "Description", style="small").pack(anchor="w", padx=30)
        self._desc = make_entry(self, placeholder="Short description", width=360)
        self._desc.pack(padx=30, pady=(4, 16))
        if genre:
            self._desc.insert(0, genre.get("description",""))

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack()
        make_button(btn_row, "Save", command=self._save).pack(side="left", padx=6)
        make_button(btn_row, "Cancel", command=self.destroy, style="ghost").pack(side="left", padx=6)

    def _save(self):
        name = self._name.get().strip()
        if not name:
            show_message(self, "Error", "Name is required.", "error"); return
        if self.on_save:
            self.on_save({"name": name, "description": self._desc.get().strip()})
        self.destroy()
