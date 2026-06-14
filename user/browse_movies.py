"""
user/browse_movies.py
User movie browser with search, filter, sort and detail view
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))


import customtkinter as ctk
import tkinter as tk
from config.database import Database
from theme import COLORS, FONTS, make_button, make_entry, make_label, make_card, show_message


class BrowseMoviesPanel(ctk.CTkFrame):
    def __init__(self, parent, user, **kwargs):
        super().__init__(parent, fg_color=COLORS["bg_dark"], corner_radius=0, **kwargs)
        self.user = user
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self._movies   = []
        self._filtered = []
        self._build()
        self._load()

    def _build(self):
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 8))
        top.grid_columnconfigure(1, weight=1)

        make_label(top, "Browse Movies", style="heading").grid(row=0, column=0, sticky="w")

        ctrl = ctk.CTkFrame(top, fg_color="transparent")
        ctrl.grid(row=0, column=1, sticky="e")

        self._search_var = tk.StringVar()
        self._search_var.trace_add("write", lambda *_: self._filter())
        make_entry(ctrl, placeholder="Search…", width=200,
                   textvariable=self._search_var).pack(side="left", padx=(0,8))

        self._genre_var = tk.StringVar(value="All Genres")
        genres = ["All Genres"] + [g["name"] for g in Database.genres().find()]
        ctk.CTkOptionMenu(ctrl, values=genres, variable=self._genre_var,
                          fg_color=COLORS["bg_input"], button_color=COLORS["bg_hover"],
                          text_color=COLORS["text_primary"], font=FONTS["body"],
                          command=lambda _: self._filter()).pack(side="left", padx=(0,8))

        self._sort_var = tk.StringVar(value="Newest")
        ctk.CTkOptionMenu(ctrl, values=["Newest","Top Rated","A–Z"],
                          variable=self._sort_var, fg_color=COLORS["bg_input"],
                          button_color=COLORS["bg_hover"], text_color=COLORS["text_primary"],
                          font=FONTS["body"], command=lambda _: self._filter()).pack(side="left")

        # Grid of movie cards
        self._grid_frame = ctk.CTkScrollableFrame(self, fg_color=COLORS["bg_dark"],
                                                   scrollbar_button_color=COLORS["bg_card"])
        self._grid_frame.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0,16))
        for c in range(4):
            self._grid_frame.grid_columnconfigure(c, weight=1)

    def _load(self):
        self._movies   = list(Database.movies().find())
        self._filter()

    def _filter(self):
        q = self._search_var.get().lower()
        g = self._genre_var.get()
        s = self._sort_var.get()

        result = [m for m in self._movies
                  if (q in m.get("title","").lower() or q in m.get("director","").lower())
                  and (g == "All Genres" or m.get("genre","") == g)]

        if s == "Top Rated":
            result.sort(key=lambda m: float(m.get("rating",0) or 0), reverse=True)
        elif s == "A–Z":
            result.sort(key=lambda m: m.get("title","").lower())

        self._filtered = result
        self._render()

    def _render(self):
        for w in self._grid_frame.winfo_children():
            w.destroy()

        if not self._filtered:
            make_label(self._grid_frame, "No movies found.", style="subhead").grid(
                row=0, column=0, columnspan=4, pady=40)
            return

        for i, m in enumerate(self._filtered):
            row, col = divmod(i, 4)
            card = make_card(self._grid_frame, cursor="hand2")
            card.grid(row=row, column=col, padx=6, pady=8, sticky="nsew")

            ctk.CTkLabel(card, text="🎬", font=("Segoe UI Emoji", 32)).pack(pady=(16,4))
            ctk.CTkLabel(card, text=m.get("title","")[:20], font=FONTS["body"],
                         text_color=COLORS["text_primary"]).pack(padx=8)
            ctk.CTkLabel(card, text=m.get("genre",""), font=FONTS["small"],
                         text_color=COLORS["text_muted"]).pack()
            ctk.CTkLabel(card, text=m.get("director","")[:20], font=FONTS["small"],
                         text_color=COLORS["text_secondary"]).pack()
            rating_row = ctk.CTkFrame(card, fg_color="transparent")
            rating_row.pack(pady=(4,8))
            ctk.CTkLabel(rating_row, text=f"⭐ {m.get('rating','N/A')}",
                         font=FONTS["small"], text_color=COLORS["accent"]).pack(side="left", padx=4)
            ctk.CTkLabel(rating_row, text=str(m.get("year","")), font=FONTS["small"],
                         text_color=COLORS["text_muted"]).pack(side="left", padx=4)

            make_button(card, "View Details", height=30, width=120,
                        command=lambda m=m: self._view_detail(m)).pack(pady=(0,12))

    def _view_detail(self, movie):
        MovieDetailDialog(self, movie, self.user)


class MovieDetailDialog(ctk.CTkToplevel):
    def __init__(self, parent, movie, user):
        super().__init__(parent)
        self.title(movie.get("title","Movie"))
        self.geometry("600x680")
        self.configure(fg_color=COLORS["bg_card"])
        self.grab_set()
        self.resizable(False, True)
        self.movie = movie
        self.user  = user

        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent",
                                        scrollbar_button_color=COLORS["bg_hover"])
        scroll.pack(fill="both", expand=True, padx=30, pady=20)

        # Hero
        ctk.CTkLabel(scroll, text="🎬", font=("Segoe UI Emoji", 52)).pack(pady=(0,8))
        ctk.CTkLabel(scroll, text=movie.get("title",""), font=("Georgia", 22, "bold"),
                     text_color=COLORS["text_primary"]).pack()

        # Meta row
        meta = ctk.CTkFrame(scroll, fg_color="transparent")
        meta.pack(pady=8)
        for text, color in [
            (f"⭐ {movie.get('rating','')}", COLORS["accent"]),
            (f"🎭 {movie.get('genre','')}", COLORS["info"]),
            (f"📅 {movie.get('year','')}", COLORS["text_secondary"]),
            (f"🌐 {movie.get('language','')}", COLORS["text_muted"]),
        ]:
            ctk.CTkLabel(meta, text=text, font=FONTS["small"], text_color=color).pack(side="left", padx=6)

        ctk.CTkFrame(scroll, height=1, fg_color=COLORS["text_muted"]).pack(fill="x", pady=12)

        for label, val in [("Director", movie.get("director","")),
                           ("Duration", f"{movie.get('duration','')} min"),
                           ("Trailer",  movie.get("trailer","N/A"))]:
            row = ctk.CTkFrame(scroll, fg_color="transparent")
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=f"{label}:", font=FONTS["small"],
                         text_color=COLORS["text_muted"], width=80).pack(side="left")
            ctk.CTkLabel(row, text=str(val), font=FONTS["body"],
                         text_color=COLORS["text_primary"]).pack(side="left")

        make_label(scroll, "Description", style="small").pack(anchor="w", pady=(12,4))
        ctk.CTkLabel(scroll, text=movie.get("description","No description available."),
                     font=FONTS["body"], text_color=COLORS["text_secondary"],
                     wraplength=520, justify="left").pack(anchor="w")

        # Action buttons
        ctk.CTkFrame(scroll, height=1, fg_color=COLORS["text_muted"]).pack(fill="x", pady=16)
        btn_row = ctk.CTkFrame(scroll, fg_color="transparent")
        btn_row.pack()
        make_button(btn_row, "❤  Add Favorite", command=self._add_fav).pack(side="left", padx=6)
        make_button(btn_row, "✏  Write Review", command=self._write_review).pack(side="left", padx=6)
        make_button(btn_row, "Close", command=self.destroy, style="ghost").pack(side="left", padx=6)

        # Existing reviews
        make_label(scroll, "User Reviews", style="subhead").pack(anchor="w", pady=(16,8))
        self._reviews_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        self._reviews_frame.pack(fill="x")
        self._load_reviews()

    def _load_reviews(self):
        for w in self._reviews_frame.winfo_children():
            w.destroy()
        reviews = list(Database.reviews().find({"movie_id": self.movie["_id"]}))
        if not reviews:
            ctk.CTkLabel(self._reviews_frame, text="No reviews yet. Be the first!",
                         font=FONTS["small"], text_color=COLORS["text_muted"]).pack()
            return
        for r in reviews:
            u = Database.users().find_one({"_id": r.get("user_id")})
            card = ctk.CTkFrame(self._reviews_frame, fg_color=COLORS["bg_input"], corner_radius=8)
            card.pack(fill="x", pady=4)
            row = ctk.CTkFrame(card, fg_color="transparent")
            row.pack(fill="x", padx=12, pady=(8,4))
            ctk.CTkLabel(row, text=u.get("username","?") if u else "?",
                         font=FONTS["body"], text_color=COLORS["text_primary"]).pack(side="left")
            ctk.CTkLabel(row, text="⭐" * int(r.get("rating",0) or 0),
                         font=FONTS["small"], text_color=COLORS["accent"]).pack(side="right")
            ctk.CTkLabel(card, text=r.get("review",""), font=FONTS["small"],
                         text_color=COLORS["text_secondary"], wraplength=500,
                         justify="left").pack(padx=12, pady=(0,8), anchor="w")

    def _add_fav(self):
        exists = Database.favorites().find_one(
            {"user_id": self.user["_id"], "movie_id": self.movie["_id"]})
        if exists:
            show_message(self, "Already Added", "This movie is already in your favorites.", "info")
        else:
            Database.favorites().insert_one(
                {"user_id": self.user["_id"], "movie_id": self.movie["_id"]})
            show_message(self, "Added", "Movie added to favorites! ❤", "success")

    def _write_review(self):
        ReviewDialog(self, self.movie, self.user, on_save=lambda: self._load_reviews())


class ReviewDialog(ctk.CTkToplevel):
    def __init__(self, parent, movie, user, on_save=None):
        super().__init__(parent)
        self.title("Write Review")
        self.geometry("480x380")
        self.configure(fg_color=COLORS["bg_card"])
        self.grab_set()
        self.resizable(False, False)
        self.movie   = movie
        self.user    = user
        self.on_save = on_save

        make_label(self, f"Review: {movie.get('title','')}", style="subhead").pack(
            pady=(20,16), padx=30, anchor="w")

        make_label(self, "Rating (1–5 stars)", style="small").pack(anchor="w", padx=30)
        self._rating = tk.IntVar(value=5)
        stars = ctk.CTkFrame(self, fg_color="transparent")
        stars.pack(anchor="w", padx=30, pady=(4,12))
        for i in range(1, 6):
            ctk.CTkRadioButton(stars, text=f"{'⭐'*i}", variable=self._rating, value=i,
                               fg_color=COLORS["accent"], font=FONTS["body"],
                               text_color=COLORS["text_primary"]).pack(side="left", padx=4)

        make_label(self, "Your Review", style="small").pack(anchor="w", padx=30)
        self._review_text = ctk.CTkTextbox(self, width=420, height=120,
                                           fg_color=COLORS["bg_input"],
                                           text_color=COLORS["text_primary"],
                                           border_color=COLORS["text_muted"],
                                           font=FONTS["body"])
        self._review_text.pack(padx=30, pady=(4,16))

        # Check for existing review
        existing = Database.reviews().find_one(
            {"movie_id": movie["_id"], "user_id": user["_id"]})
        if existing:
            self._existing = existing
            self._review_text.insert("1.0", existing.get("review",""))
            self._rating.set(int(existing.get("rating",5) or 5))
        else:
            self._existing = None

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack()
        make_button(btn_row, "Submit Review", command=self._submit).pack(side="left", padx=6)
        if self._existing:
            make_button(btn_row, "Delete Review", command=self._delete, style="danger").pack(side="left", padx=6)
        make_button(btn_row, "Cancel", command=self.destroy, style="ghost").pack(side="left", padx=6)

    def _submit(self):
        import datetime
        text   = self._review_text.get("1.0", "end").strip()
        rating = self._rating.get()
        if not text:
            show_message(self, "Error", "Please write your review.", "error"); return

        doc = {"movie_id": self.movie["_id"], "user_id": self.user["_id"],
               "rating": rating, "review": text,
               "date": datetime.datetime.now().isoformat()}

        if self._existing:
            Database.reviews().update_one({"_id": self._existing["_id"]}, {"$set": doc})
            show_message(self, "Updated", "Review updated!", "success")
        else:
            Database.reviews().insert_one(doc)
            show_message(self, "Submitted", "Review submitted! Thank you.", "success")

        if self.on_save:
            self.on_save()
        self.destroy()

    def _delete(self):
        Database.reviews().delete_one({"_id": self._existing["_id"]})
        show_message(self, "Deleted", "Review deleted.", "success")
        if self.on_save:
            self.on_save()
        self.destroy()
