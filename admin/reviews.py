"""
admin/reviews.py
Admin review management: view, filter, delete
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))


import customtkinter as ctk
import tkinter as tk
from config.database import Database
from theme import COLORS, FONTS, make_button, make_entry, make_label, show_message, ask_confirm
from admin.movies import MovieTable


class ReviewsPanel(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color=COLORS["bg_dark"], corner_radius=0, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self._reviews  = []
        self._filtered = []
        self._build()
        self._load()

    def _build(self):
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 8))
        top.grid_columnconfigure(1, weight=1)
        make_label(top, "Review Management", style="heading").grid(row=0, column=0, sticky="w")

        ctrl = ctk.CTkFrame(top, fg_color="transparent")
        ctrl.grid(row=0, column=1, sticky="e")

        self._search_var = tk.StringVar()
        self._search_var.trace_add("write", lambda *_: self._filter())
        make_entry(ctrl, placeholder="Search reviews…", width=240,
                   textvariable=self._search_var).pack(side="left", padx=(0, 8))

        self._rating_var = tk.StringVar(value="All Ratings")
        ctk.CTkOptionMenu(ctrl, values=["All Ratings","5","4","3","2","1"],
                          variable=self._rating_var, fg_color=COLORS["bg_input"],
                          button_color=COLORS["bg_hover"], text_color=COLORS["text_primary"],
                          font=FONTS["body"], command=lambda _: self._filter()).pack(side="left")

        self._table = MovieTable(self, [], [], height=460, on_select=lambda _: None)
        self._table.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 8))

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.grid(row=2, column=0, sticky="e", padx=24, pady=(0, 16))
        make_button(btn_row, "🗑  Delete Review", command=self._delete, style="danger").pack()

    def _load(self):
        raw = list(Database.reviews().find())
        # Enrich with names
        self._reviews = []
        for r in raw:
            u = Database.users().find_one({"_id": r.get("user_id")})
            m = Database.movies().find_one({"_id": r.get("movie_id")})
            r["_username"]   = u.get("username","?") if u else "?"
            r["_movie_title"] = m.get("title","?") if m else "?"
            self._reviews.append(r)
        self._filtered = self._reviews[:]
        self._refresh()

    def _refresh(self):
        cols = ["User", "Movie", "Rating", "Review", "Date"]
        rows = [[r.get("_username",""), r.get("_movie_title",""),
                 str(r.get("rating","")), r.get("review","")[:40],
                 str(r.get("date",""))[:10]] for r in self._filtered]
        self._table.columns = cols
        self._table.update_rows(rows)

    def _filter(self):
        q  = self._search_var.get().lower()
        rv = self._rating_var.get()
        self._filtered = [
            r for r in self._reviews
            if (q in r.get("_username","").lower() or q in r.get("_movie_title","").lower()
                or q in r.get("review","").lower())
            and (rv == "All Ratings" or str(r.get("rating","")) == rv)
        ]
        self._refresh()

    def _delete(self):
        idx = self._table.get_selected_index()
        if idx is None:
            show_message(self, "Select", "Select a review to delete.", "warning"); return
        rev = self._filtered[idx]
        if ask_confirm(self, "Delete Review", "Delete this review permanently?"):
            Database.reviews().delete_one({"_id": rev["_id"]})
            show_message(self, "Deleted", "Review deleted.", "success")
            self._load()
