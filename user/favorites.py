"""
user/favorites.py
User favorites list with remove functionality
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))


import customtkinter as ctk
from config.database import Database
from theme import COLORS, FONTS, make_button, make_label, make_card, show_message, ask_confirm


class FavoritesPanel(ctk.CTkFrame):
    def __init__(self, parent, user, **kwargs):
        super().__init__(parent, fg_color=COLORS["bg_dark"], corner_radius=0, **kwargs)
        self.user = user
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self._build()
        self._load()

    def _build(self):
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 8))
        make_label(top, "My Favorites ❤", style="heading").pack(anchor="w")

        self._grid = ctk.CTkScrollableFrame(self, fg_color=COLORS["bg_dark"],
                                             scrollbar_button_color=COLORS["bg_card"])
        self._grid.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 16))
        for c in range(4):
            self._grid.grid_columnconfigure(c, weight=1)

    def _load(self):
        for w in self._grid.winfo_children():
            w.destroy()

        favs = list(Database.favorites().find({"user_id": self.user["_id"]}))
        if not favs:
            ctk.CTkLabel(self._grid, text="You haven't added any favorites yet.",
                         font=FONTS["subhead"], text_color=COLORS["text_muted"]).grid(
                row=0, column=0, columnspan=4, pady=60)
            return

        for i, fav in enumerate(favs):
            m = Database.movies().find_one({"_id": fav["movie_id"]})
            if not m:
                continue
            row, col = divmod(i, 4)
            card = make_card(self._grid, cursor="hand2")
            card.grid(row=row, column=col, padx=6, pady=8, sticky="nsew")

            ctk.CTkLabel(card, text="🎬", font=("Segoe UI Emoji", 32)).pack(pady=(16,4))
            ctk.CTkLabel(card, text=m.get("title","")[:20], font=FONTS["body"],
                         text_color=COLORS["text_primary"]).pack(padx=8)
            ctk.CTkLabel(card, text=m.get("genre",""), font=FONTS["small"],
                         text_color=COLORS["text_muted"]).pack()
            ctk.CTkLabel(card, text=f"⭐ {m.get('rating','')}", font=FONTS["small"],
                         text_color=COLORS["accent"]).pack(pady=4)
            make_button(card, "💔 Remove", height=28, width=110, style="danger",
                        command=lambda fid=fav["_id"]: self._remove(fid)).pack(pady=(0,12))

    def _remove(self, fav_id):
        if ask_confirm(self, "Remove Favorite", "Remove this movie from favorites?"):
            Database.favorites().delete_one({"_id": fav_id})
            self._load()
