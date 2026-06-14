"""
user/reviews.py
User's own reviews with edit and delete
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))


import customtkinter as ctk
import datetime
from config.database import Database
from theme import COLORS, FONTS, make_button, make_label, make_card, show_message, ask_confirm


class UserReviewsPanel(ctk.CTkFrame):
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
        make_label(top, "My Reviews ⭐", style="heading").pack(anchor="w")

        self._scroll = ctk.CTkScrollableFrame(self, fg_color=COLORS["bg_dark"],
                                               scrollbar_button_color=COLORS["bg_card"])
        self._scroll.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 16))
        self._scroll.grid_columnconfigure(0, weight=1)

    def _load(self):
        for w in self._scroll.winfo_children():
            w.destroy()

        reviews = list(Database.reviews().find({"user_id": self.user["_id"]}))
        if not reviews:
            ctk.CTkLabel(self._scroll, text="You haven't written any reviews yet.",
                         font=FONTS["subhead"], text_color=COLORS["text_muted"]).pack(pady=60)
            return

        for rev in reviews:
            m = Database.movies().find_one({"_id": rev.get("movie_id")})
            card = make_card(self._scroll)
            card.grid(sticky="ew", pady=6)

            header = ctk.CTkFrame(card, fg_color="transparent")
            header.pack(fill="x", padx=16, pady=(12,0))

            ctk.CTkLabel(header, text=m.get("title","Unknown Movie") if m else "Unknown",
                         font=FONTS["subhead"], text_color=COLORS["text_primary"]).pack(side="left")
            stars = "⭐" * int(rev.get("rating",0) or 0)
            ctk.CTkLabel(header, text=stars, font=FONTS["body"],
                         text_color=COLORS["accent"]).pack(side="right")

            ctk.CTkLabel(card, text=rev.get("review",""), font=FONTS["body"],
                         text_color=COLORS["text_secondary"], wraplength=700,
                         justify="left").pack(padx=16, pady=(6,4), anchor="w")

            footer = ctk.CTkFrame(card, fg_color="transparent")
            footer.pack(fill="x", padx=16, pady=(0,12))
            ctk.CTkLabel(footer, text=str(rev.get("date",""))[:10], font=FONTS["small"],
                         text_color=COLORS["text_muted"]).pack(side="left")

            make_button(footer, "✏ Edit", height=28, style="ghost",
                        command=lambda r=rev, mv=m: self._edit(r, mv)).pack(side="right", padx=4)
            make_button(footer, "🗑 Delete", height=28, style="danger",
                        command=lambda r=rev: self._delete(r)).pack(side="right", padx=4)

    def _edit(self, rev, movie):
        if not movie:
            return
        EditReviewDialog(self, rev, movie, on_save=self._load)

    def _delete(self, rev):
        if ask_confirm(self, "Delete Review", "Delete this review permanently?"):
            Database.reviews().delete_one({"_id": rev["_id"]})
            self._load()


class EditReviewDialog(ctk.CTkToplevel):
    def __init__(self, parent, review, movie, on_save=None):
        super().__init__(parent)
        self.title("Edit Review")
        self.geometry("480x340")
        self.configure(fg_color=COLORS["bg_card"])
        self.grab_set()
        self.resizable(False, False)
        self.review  = review
        self.on_save = on_save

        import tkinter as tk
        make_label(self, f"Editing review for: {movie.get('title','')}", style="subhead").pack(
            pady=(20, 12), padx=30, anchor="w")

        make_label(self, "Rating (1–5)", style="small").pack(anchor="w", padx=30)
        self._rating = tk.IntVar(value=int(review.get("rating",5) or 5))
        stars = ctk.CTkFrame(self, fg_color="transparent")
        stars.pack(anchor="w", padx=30, pady=(4, 12))
        for i in range(1, 6):
            ctk.CTkRadioButton(stars, text=f"{'⭐'*i}", variable=self._rating, value=i,
                               fg_color=COLORS["accent"], font=FONTS["body"],
                               text_color=COLORS["text_primary"]).pack(side="left", padx=4)

        make_label(self, "Review Text", style="small").pack(anchor="w", padx=30)
        self._text = ctk.CTkTextbox(self, width=420, height=100,
                                    fg_color=COLORS["bg_input"],
                                    text_color=COLORS["text_primary"],
                                    font=FONTS["body"])
        self._text.pack(padx=30, pady=(4, 16))
        self._text.insert("1.0", review.get("review",""))

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack()
        make_button(btn_row, "Save Changes", command=self._save).pack(side="left", padx=6)
        make_button(btn_row, "Cancel", command=self.destroy, style="ghost").pack(side="left", padx=6)

    def _save(self):
        text = self._text.get("1.0", "end").strip()
        if not text:
            show_message(self, "Error", "Review text required.", "error"); return
        Database.reviews().update_one(
            {"_id": self.review["_id"]},
            {"$set": {"review": text, "rating": self._rating.get(),
                      "date": datetime.datetime.now().isoformat()}})
        show_message(self, "Saved", "Review updated!", "success")
        if self.on_save:
            self.on_save()
        self.destroy()
