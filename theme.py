"""
theme.py  –  Shared design tokens and helper widgets
"""

import customtkinter as ctk

# ─── Colour Palette ────────────────────────────────────────────────────────────
COLORS = {
    # Backgrounds
    "bg_dark":      "#0D0F14",
    "bg_card":      "#161B25",
    "bg_sidebar":   "#111520",
    "bg_input":     "#1E2535",
    "bg_hover":     "#1E2A3A",

    # Accents
    "accent":       "#E8A020",
    "accent_dark":  "#C4851A",
    "accent_light": "#F2C060",

    # Text
    "text_primary":   "#F0F2F5",
    "text_secondary": "#8A93A8",
    "text_muted":     "#4A5568",

    # Status
    "success":  "#2ECC71",
    "warning":  "#F39C12",
    "danger":   "#E74C3C",
    "info":     "#3498DB",

    # Sidebar active
    "sidebar_active": "#1E2A3A",
    "sidebar_text":   "#C8D0E0",
}

FONTS = {
    "title":    ("Georgia", 26, "bold"),
    "heading":  ("Georgia", 18, "bold"),
    "subhead":  ("Trebuchet MS", 14, "bold"),
    "body":     ("Trebuchet MS", 12),
    "small":    ("Trebuchet MS", 10),
    "mono":     ("Courier New", 11),
    "sidebar":  ("Trebuchet MS", 13),
}


def configure_ctk():
    """Apply global CTk appearance."""
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")


# ─── Reusable Widget Helpers ──────────────────────────────────────────────────

def make_card(parent, **kwargs):
    defaults = dict(fg_color=COLORS["bg_card"], corner_radius=12)
    defaults.update(kwargs)
    return ctk.CTkFrame(parent, **defaults)


def make_button(parent, text, command=None, style="primary", **kwargs):
    styles = {
        "primary": dict(fg_color=COLORS["accent"], hover_color=COLORS["accent_dark"],
                        text_color="#000000"),
        "danger":  dict(fg_color=COLORS["danger"],  hover_color="#C0392B",
                        text_color="#FFFFFF"),
        "ghost":   dict(fg_color="transparent", hover_color=COLORS["bg_hover"],
                        text_color=COLORS["text_secondary"],
                        border_width=1, border_color=COLORS["text_muted"]),
        "success": dict(fg_color=COLORS["success"], hover_color="#27AE60",
                        text_color="#FFFFFF"),
    }
    cfg = dict(text=text, command=command, font=FONTS["body"],
               corner_radius=8, height=36)
    cfg.update(styles.get(style, styles["primary"]))
    cfg.update(kwargs)
    return ctk.CTkButton(parent, **cfg)


def make_entry(parent, placeholder="", show=None, **kwargs):
    cfg = dict(
        placeholder_text=placeholder,
        fg_color=COLORS["bg_input"],
        border_color=COLORS["text_muted"],
        text_color=COLORS["text_primary"],
        placeholder_text_color=COLORS["text_muted"],
        font=FONTS["body"],
        corner_radius=8,
        height=38,
    )
    if show:
        cfg["show"] = show
    cfg.update(kwargs)
    return ctk.CTkEntry(parent, **cfg)


def make_label(parent, text, style="body", **kwargs):
    font_map = {
        "title":   FONTS["title"],
        "heading": FONTS["heading"],
        "subhead": FONTS["subhead"],
        "body":    FONTS["body"],
        "small":   FONTS["small"],
        "muted":   FONTS["small"],
    }
    color_map = {
        "title":   COLORS["text_primary"],
        "heading": COLORS["text_primary"],
        "subhead": COLORS["text_primary"],
        "body":    COLORS["text_primary"],
        "small":   COLORS["text_secondary"],
        "muted":   COLORS["text_muted"],
    }
    cfg = dict(text=text, font=font_map.get(style, FONTS["body"]),
               text_color=color_map.get(style, COLORS["text_primary"]))
    cfg.update(kwargs)
    return ctk.CTkLabel(parent, **cfg)


def show_message(parent, title, message, msg_type="info"):
    """Simple modal message box."""
    import tkinter as tk
    colors = {
        "info":    COLORS["info"],
        "success": COLORS["success"],
        "error":   COLORS["danger"],
        "warning": COLORS["warning"],
    }
    win = ctk.CTkToplevel(parent)
    win.title(title)
    win.geometry("420x200")
    win.configure(fg_color=COLORS["bg_card"])
    win.grab_set()
    win.resizable(False, False)

    # Center
    win.update_idletasks()
    x = parent.winfo_rootx() + (parent.winfo_width() - 420) // 2
    y = parent.winfo_rooty() + (parent.winfo_height() - 200) // 2
    win.geometry(f"+{x}+{y}")

    bar = ctk.CTkFrame(win, height=4, fg_color=colors.get(msg_type, COLORS["info"]),
                       corner_radius=0)
    bar.pack(fill="x")

    ctk.CTkLabel(win, text=title, font=FONTS["subhead"],
                 text_color=COLORS["text_primary"]).pack(pady=(20, 4))
    ctk.CTkLabel(win, text=message, font=FONTS["body"],
                 text_color=COLORS["text_secondary"],
                 wraplength=380).pack(pady=(0, 16))
    make_button(win, "OK", command=win.destroy).pack()


def ask_confirm(parent, title, message):
    """Returns True if user clicks Yes."""
    import tkinter as tk
    result = [False]

    win = ctk.CTkToplevel(parent)
    win.title(title)
    win.geometry("420x200")
    win.configure(fg_color=COLORS["bg_card"])
    win.grab_set()
    win.resizable(False, False)

    win.update_idletasks()
    x = parent.winfo_rootx() + (parent.winfo_width() - 420) // 2
    y = parent.winfo_rooty() + (parent.winfo_height() - 200) // 2
    win.geometry(f"+{x}+{y}")

    bar = ctk.CTkFrame(win, height=4, fg_color=COLORS["warning"], corner_radius=0)
    bar.pack(fill="x")

    ctk.CTkLabel(win, text=title, font=FONTS["subhead"],
                 text_color=COLORS["text_primary"]).pack(pady=(20, 4))
    ctk.CTkLabel(win, text=message, font=FONTS["body"],
                 text_color=COLORS["text_secondary"],
                 wraplength=380).pack(pady=(0, 16))

    btn_frame = ctk.CTkFrame(win, fg_color="transparent")
    btn_frame.pack()

    def yes():
        result[0] = True
        win.destroy()

    make_button(btn_frame, "Yes, Delete", command=yes, style="danger").pack(side="left", padx=6)
    make_button(btn_frame, "Cancel", command=win.destroy, style="ghost").pack(side="left", padx=6)

    win.wait_window()
    return result[0]
