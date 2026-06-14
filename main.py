"""
main.py
CineVault – Movie Management System
Entry point: splash screen → login
"""

import customtkinter as ctk
import sys
import os
import time
import threading

# ── Make sure project root is in path ──────────────────────────────────────────
sys.path.insert(0, os.path.dirname(__file__))

from theme import COLORS, FONTS, configure_ctk
from config.database import Database


class SplashScreen(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("CineVault")
        self.geometry("520x320")
        self.resizable(False, False)
        self.configure(fg_color=COLORS["bg_dark"])

        # Center on screen
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x  = (sw - 520) // 2
        y  = (sh - 320) // 2
        self.geometry(f"520x320+{x}+{y}")
        self.overrideredirect(True)

        # Accent border
        border = ctk.CTkFrame(self, fg_color=COLORS["accent"], corner_radius=0)
        border.place(x=0, y=0, width=520, height=4)

        ctk.CTkLabel(self, text="🎬", font=("Segoe UI Emoji", 56)).pack(pady=(40, 8))
        ctk.CTkLabel(self, text="CineVault",
                     font=("Georgia", 32, "bold"), text_color=COLORS["accent"]).pack()
        ctk.CTkLabel(self, text="Movie Management System",
                     font=FONTS["body"], text_color=COLORS["text_secondary"]).pack(pady=4)

        self._status = ctk.CTkLabel(self, text="Initialising…",
                                    font=FONTS["small"], text_color=COLORS["text_muted"])
        self._status.pack(pady=(16, 8))

        self._bar = ctk.CTkProgressBar(self, width=300, fg_color=COLORS["bg_card"],
                                       progress_color=COLORS["accent"])
        self._bar.pack()
        self._bar.set(0)

        self._run()

    def _run(self):
        def task():
            steps = [
                (0.2,  "Connecting to MongoDB…"),
                (0.5,  "Loading collections…"),
                (0.8,  "Preparing interface…"),
                (1.0,  "Ready!"),
            ]
            for pct, msg in steps:
                time.sleep(0.5)
                self.after(0, lambda p=pct, m=msg: (
                    self._bar.set(p),
                    self._status.configure(text=m)
                ))
            time.sleep(0.4)
            self.after(0, self._launch)

        threading.Thread(target=task, daemon=True).start()

    def _launch(self):
        ok = Database.connect()
        self.destroy()
        if not ok:
            import tkinter.messagebox as mb
            mb.showerror("Connection Error",
                         "Could not connect to MongoDB.\n"
                         "Please ensure MongoDB is running on localhost:27017\n"
                         "and try again.")
            sys.exit(1)
        from authentication.login import LoginWindow
        LoginWindow().mainloop()


def main():
    configure_ctk()
    SplashScreen().mainloop()


if __name__ == "__main__":
    main()
