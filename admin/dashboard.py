"""
admin/dashboard.py
Admin dashboard with stats cards and sidebar navigation
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))


import customtkinter as ctk
from base_dashboard import BaseDashboard
from theme import COLORS, FONTS, make_label, make_card
from config.database import Database


class AdminDashboard(BaseDashboard):
    WINDOW_TITLE = "CineVault – Admin Dashboard"
    WINDOW_SIZE = "1340x780"
    MENU_ITEMS = [
        ("📊", "Dashboard",  "show_dashboard"),
        ("🎬", "Movies",     "show_movies"),
        ("👥", "Users",      "show_users"),
        ("🏷", "Genres",     "show_genres"),
        ("⭐", "Reviews",    "show_reviews"),
        ("📑", "Reports",    "show_reports"),
        ("⚙", "Settings",   "show_settings"),
        ("🚪", "Logout",     "logout"),
    ]

    def __init__(self, user):
        super().__init__(user)
        self.show_dashboard()

    # ─── Sections ─────────────────────────────────────────────────────────────
    def show_dashboard(self):
        self._set_active("Dashboard")
        self.clear_content()
        frame = ctk.CTkScrollableFrame(self.content, fg_color=COLORS["bg_dark"],
                                       scrollbar_button_color=COLORS["bg_card"])
        frame.grid(row=0, column=0, sticky="nsew", padx=24, pady=20)
        frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        # Header
        make_label(frame, "Dashboard Overview", style="heading").grid(
            row=0, column=0, columnspan=5, sticky="w", pady=(0, 20))

        # Stats
        stats = self._get_stats()
        cards_data = [
            ("🎬", "Total Movies",  stats["movies"],  COLORS["accent"]),
            ("👥", "Total Users",   stats["users"],   COLORS["info"]),
            ("🏷", "Genres",        stats["genres"],  COLORS["success"]),
            ("⭐", "Reviews",       stats["reviews"], COLORS["warning"]),
            ("📈", "Avg Rating",    f"{stats['avg_rating']:.1f}", "#9B59B6"),
        ]
        for col, (icon, title, val, color) in enumerate(cards_data):
            self._stat_card(frame, icon, title, val, color, row=1, col=col)

        # Recent movies table
        make_label(frame, "Recent Movies", style="subhead").grid(
            row=2, column=0, columnspan=5, sticky="w", pady=(28, 10))
        self._recent_movies_table(frame, row=3)

        # Recent users
        make_label(frame, "Recent Users", style="subhead").grid(
            row=4, column=0, columnspan=5, sticky="w", pady=(24, 10))
        self._recent_users_table(frame, row=5)

    def _stat_card(self, parent, icon, title, value, color, row, col):
        card = make_card(parent)
        card.grid(row=row, column=col, padx=6, pady=6, sticky="ew")

        bar = ctk.CTkFrame(card, height=4, fg_color=color, corner_radius=0)
        bar.pack(fill="x")

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(padx=16, pady=12)

        ctk.CTkLabel(inner, text=icon, font=("Segoe UI Emoji", 24)).pack(anchor="w")
        ctk.CTkLabel(inner, text=str(value), font=("Georgia", 26, "bold"),
                     text_color=color).pack(anchor="w", pady=(4, 0))
        ctk.CTkLabel(inner, text=title, font=FONTS["small"],
                     text_color=COLORS["text_secondary"]).pack(anchor="w")

    def _get_stats(self):
        movies  = Database.movies().count_documents({})
        users   = Database.users().count_documents({})
        genres  = Database.genres().count_documents({})
        reviews = Database.reviews().count_documents({})
        ratings = list(Database.movies().find({}, {"rating": 1}))
        avg = (sum(float(r.get("rating", 0) or 0) for r in ratings) / len(ratings)
               if ratings else 0)
        return dict(movies=movies, users=users, genres=genres, reviews=reviews, avg_rating=avg)

    def _recent_movies_table(self, parent, row):
        from admin.movies import MovieTable
        movies = list(Database.movies().find().sort("_id", -1).limit(5))
        cols = ["Title", "Genre", "Director", "Year", "Rating"]
        rows = [[m.get("title",""), m.get("genre",""), m.get("director",""),
                 str(m.get("year","")), str(m.get("rating",""))] for m in movies]
        MovieTable(parent, cols, rows, height=160).grid(
            row=row, column=0, columnspan=5, sticky="ew")

    def _recent_users_table(self, parent, row):
        from admin.movies import MovieTable
        users = list(Database.users().find().sort("_id", -1).limit(5))
        cols  = ["Name", "Username", "Email", "Role", "Status"]
        rows  = [[u.get("name",""), u.get("username",""), u.get("email",""),
                  u.get("role",""), u.get("status","")] for u in users]
        MovieTable(parent, cols, rows, height=160).grid(
            row=row, column=0, columnspan=5, sticky="ew")

    # ─── Navigation targets ───────────────────────────────────────────────────
    def show_movies(self):
        self._set_active("Movies")
        self.clear_content()
        from admin.movies import MoviesPanel
        MoviesPanel(self.content, self.user).grid(row=0, column=0, sticky="nsew")

    def show_users(self):
        self._set_active("Users")
        self.clear_content()
        from admin.users import UsersPanel
        UsersPanel(self.content, self.user).grid(row=0, column=0, sticky="nsew")

    def show_genres(self):
        self._set_active("Genres")
        self.clear_content()
        from admin.genres import GenresPanel
        GenresPanel(self.content).grid(row=0, column=0, sticky="nsew")

    def show_reviews(self):
        self._set_active("Reviews")
        self.clear_content()
        from admin.reviews import ReviewsPanel
        ReviewsPanel(self.content).grid(row=0, column=0, sticky="nsew")

    def show_reports(self):
        self._set_active("Reports")
        self.clear_content()
        from admin.reports import ReportsPanel
        ReportsPanel(self.content).grid(row=0, column=0, sticky="nsew")

    def show_settings(self):
        self._set_active("Settings")
        self.clear_content()
        _settings_placeholder(self.content)

    def logout(self):
        from authentication.login import LoginWindow
        self.destroy()
        LoginWindow().mainloop()


def _settings_placeholder(parent):
    lbl = ctk.CTkLabel(parent, text="⚙  Settings coming soon",
                        font=FONTS["heading"], text_color=COLORS["text_muted"])
    lbl.place(relx=0.5, rely=0.5, anchor="center")
