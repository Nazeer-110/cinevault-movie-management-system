"""
admin/movies.py
Full CRUD for movies + reusable MovieTable widget
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))


import customtkinter as ctk
import tkinter as tk
from bson import ObjectId
from config.database import Database
from theme import COLORS, FONTS, make_button, make_entry, make_label, make_card, show_message, ask_confirm


# ─── Reusable table widget ────────────────────────────────────────────────────
class MovieTable(ctk.CTkFrame):
    """Simple themed table built from CTkLabels."""

    HEADER_BG = COLORS["bg_sidebar"]
    ROW_BG    = COLORS["bg_card"]
    ALT_BG    = "#12161F"
    SEL_BG    = COLORS["bg_hover"]

    def __init__(self, parent, columns, rows, height=300, on_select=None, **kwargs):
        super().__init__(parent, fg_color=COLORS["bg_card"], corner_radius=10, **kwargs)
        self.columns   = columns
        self.all_rows  = rows
        self.on_select = on_select
        self._sel_idx  = None
        self._row_widgets = []
        self._build(height)

    def _build(self, height):
        header = ctk.CTkFrame(self, fg_color=self.HEADER_BG, corner_radius=0)
        header.pack(fill="x")
        for i, col in enumerate(self.columns):
            ctk.CTkLabel(header, text=col, font=FONTS["small"],
                         text_color=COLORS["accent"],
                         width=self._col_w(i)).pack(side="left", padx=8, pady=6)

        self._scroll = ctk.CTkScrollableFrame(self, fg_color="transparent",
                                              height=height,
                                              scrollbar_button_color=COLORS["bg_hover"])
        self._scroll.pack(fill="both", expand=True)
        self._render_rows(self.all_rows)

    def _col_w(self, i):
        ws = [180, 120, 130, 70, 80, 90, 80, 100]
        return ws[i] if i < len(ws) else 100

    def _render_rows(self, rows):
        for w in self._scroll.winfo_children():
            w.destroy()
        self._row_widgets = []
        for idx, row in enumerate(rows):
            bg = self.ROW_BG if idx % 2 == 0 else self.ALT_BG
            r  = ctk.CTkFrame(self._scroll, fg_color=bg, corner_radius=0)
            r.pack(fill="x")
            for ci, cell in enumerate(row):
                ctk.CTkLabel(r, text=str(cell)[:30], font=FONTS["small"],
                             text_color=COLORS["text_primary"],
                             width=self._col_w(ci)).pack(side="left", padx=8, pady=5)
            r.bind("<Button-1>", lambda e, i=idx: self._select(i))
            for child in r.winfo_children():
                child.bind("<Button-1>", lambda e, i=idx: self._select(i))
            self._row_widgets.append(r)

    def _select(self, idx):
        if self._sel_idx is not None and self._sel_idx < len(self._row_widgets):
            orig = self.ROW_BG if self._sel_idx % 2 == 0 else self.ALT_BG
            self._row_widgets[self._sel_idx].configure(fg_color=orig)
        self._sel_idx = idx
        self._row_widgets[idx].configure(fg_color=self.SEL_BG)
        if self.on_select:
            self.on_select(idx)

    def update_rows(self, rows):
        self.all_rows = rows
        self._render_rows(rows)

    def get_selected_index(self):
        return self._sel_idx


# ─── Movies Panel ─────────────────────────────────────────────────────────────
class MoviesPanel(ctk.CTkFrame):
    def __init__(self, parent, user=None, **kwargs):
        super().__init__(parent, fg_color=COLORS["bg_dark"], corner_radius=0, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.user = user
        self._movies = []
        self._filtered = []
        self._build()
        self._load()

    def _build(self):
        # Top bar
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 8))
        top.grid_columnconfigure(1, weight=1)

        make_label(top, "Movie Management", style="heading").grid(row=0, column=0, sticky="w")

        controls = ctk.CTkFrame(top, fg_color="transparent")
        controls.grid(row=0, column=1, sticky="e")

        self._search_var = tk.StringVar()
        self._search_var.trace_add("write", lambda *_: self._filter())
        srch = make_entry(controls, placeholder="Search movies…", width=220,
                          textvariable=self._search_var)
        srch.pack(side="left", padx=(0, 8))

        self._genre_var = tk.StringVar(value="All Genres")
        genres = ["All Genres"] + [g["name"] for g in Database.genres().find()]
        self._genre_menu = ctk.CTkOptionMenu(
            controls, values=genres, variable=self._genre_var,
            fg_color=COLORS["bg_input"], button_color=COLORS["bg_hover"],
            text_color=COLORS["text_primary"], font=FONTS["body"],
            command=lambda _: self._filter())
        self._genre_menu.pack(side="left", padx=(0, 8))

        make_button(controls, "+ Add Movie", command=self._add_movie).pack(side="left")

        # Table
        self._table = MovieTable(self, [], [], height=460,
                                 on_select=self._on_select)
        self._table.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 8))

        # Action buttons
        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.grid(row=2, column=0, sticky="e", padx=24, pady=(0, 16))
        make_button(btn_row, "✏  Edit", command=self._edit_movie, style="ghost").pack(side="left", padx=4)
        make_button(btn_row, "🗑  Delete", command=self._delete_movie, style="danger").pack(side="left", padx=4)

    def _load(self):
        self._movies = list(Database.movies().find())
        self._filtered = self._movies[:]
        self._refresh_table()

    def _refresh_table(self):
        cols = ["Title", "Genre", "Director", "Year", "Language", "Rating"]
        rows = [[m.get("title",""), m.get("genre",""), m.get("director",""),
                 str(m.get("year","")), m.get("language",""), str(m.get("rating",""))]
                for m in self._filtered]
        self._table.columns = cols
        self._table.update_rows(rows)

    def _filter(self):
        q = self._search_var.get().lower()
        g = self._genre_var.get()
        self._filtered = [
            m for m in self._movies
            if (q in m.get("title","").lower() or q in m.get("director","").lower())
            and (g == "All Genres" or m.get("genre","") == g)
        ]
        self._refresh_table()

    def _on_select(self, idx):
        self._sel_idx = idx

    def _add_movie(self):
        MovieFormDialog(self, title="Add Movie", on_save=self._save_new)

    def _save_new(self, data):
        Database.movies().insert_one(data)
        show_message(self, "Success", "Movie added successfully!", "success")
        self._load()

    def _edit_movie(self):
        idx = self._table.get_selected_index()
        if idx is None:
            show_message(self, "Select", "Please select a movie to edit.", "warning"); return
        movie = self._filtered[idx]
        MovieFormDialog(self, title="Edit Movie", movie=movie,
                        on_save=lambda d: self._save_edit(movie["_id"], d))

    def _save_edit(self, mid, data):
        Database.movies().update_one({"_id": mid}, {"$set": data})
        show_message(self, "Updated", "Movie updated successfully!", "success")
        self._load()

    def _delete_movie(self):
        idx = self._table.get_selected_index()
        if idx is None:
            show_message(self, "Select", "Please select a movie to delete.", "warning"); return
        movie = self._filtered[idx]
        if ask_confirm(self, "Delete Movie",
                       f"Delete '{movie.get('title')}'? This cannot be undone."):
            Database.movies().delete_one({"_id": movie["_id"]})
            show_message(self, "Deleted", "Movie deleted.", "success")
            self._load()


# ─── Movie Form Dialog ────────────────────────────────────────────────────────
class MovieFormDialog(ctk.CTkToplevel):
    def __init__(self, parent, title="Movie", movie=None, on_save=None):
        super().__init__(parent)
        self.title(title)
        self.geometry("560x680")
        self.configure(fg_color=COLORS["bg_card"])
        self.grab_set()
        self.resizable(False, False)
        self.on_save = on_save
        self.movie = movie or {}

        self._build()
        if movie:
            self._populate(movie)

    def _build(self):
        make_label(self, self.title(), style="subhead").pack(pady=(20, 4), padx=30, anchor="w")
        ctk.CTkFrame(self, height=1, fg_color=COLORS["text_muted"]).pack(fill="x", padx=30, pady=(0, 16))

        self._scroll = ctk.CTkScrollableFrame(self, fg_color="transparent",
                                              scrollbar_button_color=COLORS["bg_hover"])
        self._scroll.pack(fill="both", expand=True, padx=30)

        self._entries = {}
        fields = [
            ("title",       "Movie Title",  False),
            ("genre",       "Genre",        False),
            ("director",    "Director",     False),
            ("year",        "Release Year", False),
            ("duration",    "Duration (min)", False),
            ("language",    "Language",     False),
            ("rating",      "Rating (0-10)", False),
            ("poster",      "Poster URL",   False),
            ("trailer",     "Trailer Link", False),
        ]
        for key, label, _ in fields:
            make_label(self._scroll, label, style="small").pack(anchor="w", pady=(8, 3))
            e = make_entry(self._scroll, placeholder=label, width=480)
            e.pack()
            self._entries[key] = e

        make_label(self._scroll, "Description", style="small").pack(anchor="w", pady=(8, 3))
        self._desc = ctk.CTkTextbox(self._scroll, width=480, height=80,
                                    fg_color=COLORS["bg_input"],
                                    text_color=COLORS["text_primary"],
                                    border_color=COLORS["text_muted"],
                                    font=FONTS["body"])
        self._desc.pack()

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(pady=16)
        make_button(btn_row, "Save Movie", command=self._save).pack(side="left", padx=6)
        make_button(btn_row, "Cancel", command=self.destroy, style="ghost").pack(side="left", padx=6)

    def _populate(self, m):
        for key, entry in self._entries.items():
            entry.insert(0, str(m.get(key, "")))
        self._desc.insert("1.0", m.get("description", ""))

    def _save(self):
        data = {k: e.get().strip() for k, e in self._entries.items()}
        data["description"] = self._desc.get("1.0", "end").strip()
        if not data.get("title"):
            show_message(self, "Error", "Movie title is required.", "error"); return
        if self.on_save:
            self.on_save(data)
        self.destroy()
