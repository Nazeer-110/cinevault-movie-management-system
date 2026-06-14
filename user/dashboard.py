"""
user/dashboard.py
User dashboard with sidebar navigation
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))


import customtkinter as ctk
from base_dashboard import BaseDashboard
from theme import COLORS, FONTS, make_label, make_card
from config.database import Database


class UserDashboard(BaseDashboard):
    WINDOW_TITLE = "CineVault – User Dashboard"
    WINDOW_SIZE  = "1200x740"
    MENU_ITEMS   = [
        ("🏠", "Home",          "show_home"),
        ("🎬", "Browse Movies", "show_browse"),
        ("❤",  "My Favorites",  "show_favorites"),
        ("⭐", "My Reviews",   "show_reviews"),
        ("👤", "Profile",       "show_profile"),
        ("🚪", "Logout",        "logout"),
    ]

    def __init__(self, user):
        super().__init__(user)
        self.show_home()

    def show_home(self):
        self._set_active("Home")
        self.clear_content()
        frame = ctk.CTkScrollableFrame(self.content, fg_color=COLORS["bg_dark"],
                                       scrollbar_button_color=COLORS["bg_card"])
        frame.grid(row=0, column=0, sticky="nsew", padx=24, pady=20)
        frame.grid_columnconfigure((0,1,2), weight=1)

        # Greeting
        make_label(frame, f"Welcome back, {self.user.get('name','').split()[0]}! 👋",
                   style="heading").grid(row=0, column=0, columnspan=3, sticky="w", pady=(0,20))

        # Stats cards
        total_movies  = Database.movies().count_documents({})
        my_favorites  = Database.favorites().count_documents({"user_id": self.user["_id"]})
        my_reviews    = Database.reviews().count_documents({"user_id": self.user["_id"]})

        for col, (icon, lbl, val, color) in enumerate([
            ("🎬", "Total Movies",  total_movies,  COLORS["accent"]),
            ("❤",  "My Favorites", my_favorites,  COLORS["danger"]),
            ("⭐", "My Reviews",   my_reviews,    COLORS["warning"]),
        ]):
            card = make_card(frame)
            card.grid(row=1, column=col, padx=6, sticky="ew")
            ctk.CTkFrame(card, height=4, fg_color=color, corner_radius=0).pack(fill="x")
            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(padx=16, pady=12)
            ctk.CTkLabel(inner, text=icon, font=("Segoe UI Emoji", 24)).pack(anchor="w")
            ctk.CTkLabel(inner, text=str(val), font=("Georgia", 26, "bold"),
                         text_color=color).pack(anchor="w", pady=(4,0))
            ctk.CTkLabel(inner, text=lbl, font=FONTS["small"],
                         text_color=COLORS["text_secondary"]).pack(anchor="w")

        # Recently added movies
        make_label(frame, "Recently Added", style="subhead").grid(
            row=2, column=0, columnspan=3, sticky="w", pady=(28, 12))
        movies = list(Database.movies().find().sort("_id", -1).limit(6))
        for i, m in enumerate(movies):
            card = make_card(frame)
            card.grid(row=3 + i//3, column=i%3, padx=6, pady=6, sticky="nsew")
            ctk.CTkLabel(card, text="🎬", font=("Segoe UI Emoji", 28)).pack(pady=(16,4))
            ctk.CTkLabel(card, text=m.get("title","")[:22], font=FONTS["body"],
                         text_color=COLORS["text_primary"]).pack(padx=8)
            ctk.CTkLabel(card, text=m.get("genre",""), font=FONTS["small"],
                         text_color=COLORS["text_muted"]).pack()
            ctk.CTkLabel(card, text=f"⭐ {m.get('rating','')}", font=FONTS["small"],
                         text_color=COLORS["accent"]).pack(pady=(4,12))

    def show_browse(self):
        self._set_active("Browse Movies")
        self.clear_content()
        from user.browse_movies import BrowseMoviesPanel
        BrowseMoviesPanel(self.content, self.user).grid(row=0, column=0, sticky="nsew")

    def show_favorites(self):
        self._set_active("My Favorites")
        self.clear_content()
        from user.favorites import FavoritesPanel
        FavoritesPanel(self.content, self.user).grid(row=0, column=0, sticky="nsew")

    def show_reviews(self):
        self._set_active("My Reviews")
        self.clear_content()
        from user.reviews import UserReviewsPanel
        UserReviewsPanel(self.content, self.user).grid(row=0, column=0, sticky="nsew")

    def show_profile(self):
        self._set_active("Profile")
        self.clear_content()
        from user.profile import ProfilePanel
        ProfilePanel(self.content, self.user).grid(row=0, column=0, sticky="nsew")

    def logout(self):
        from authentication.login import LoginWindow
        self.destroy()
        LoginWindow().mainloop()
