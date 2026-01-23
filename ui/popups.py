import customtkinter as ctk
from ui.helpers import add_buttons, create_label, create_title, get_colors
from customtkinter import CENTER

COLORS = get_colors()
ACCENT_COLOR = COLORS['accent_color']
HOVER_COLOR = COLORS['hover_color']
TEXT_COLOR = COLORS['text_color']

def simple_alert(root, title: str, message: str):
    win = ctk.CTkToplevel(root)
    win.title(title)
    win.geometry("300x200")
    win.transient(root)
    win.grab_set()
    title = create_title(win, title)
    title.pack(pady=8)
    create_label(win, message).pack(pady=12)
    add_buttons(win, text="OK", colors_dict=COLORS,command=win.destroy).pack(pady=6)
    root.wait_window(win)

def tell_unlock_required(root):
    simple_alert(root, "Unlock Required", "Please unlock the vault to \naccess settings.")

def empty_fields_alert(root):
    simple_alert(root, "Empty fields", "Empty fields detected. Please \nfill out all fields and try again.")

def password_mismatch_alert(root):
    simple_alert(root, "Passwords dont match", "The passwords entered do not match. \n Please try again.")

def success_alert(root, message: str):
    simple_alert(root, "Success", message)


def confirm_replace(root, site: str, username: str) -> bool:
    """Ask user whether to replace an existing entry. Returns True to replace."""
    win = ctk.CTkToplevel(root)
    win.title("Replace entry?")
    win.geometry("350x180")
    win.transient(root)
    win.grab_set()
    title = create_title(win, "Replace entry?")
    title.pack(pady=8)
    create_label(win, f"An entry for '{site}' with username \n '{username}' already exists.").pack(pady=8)

    result = {"replace": False}

    def do_replace():
        result["replace"] = True
        win.destroy()

    def do_cancel():
        result["replace"] = False
        win.destroy()

    # two buttons: Replace and Cancel
    btn_frame = ctk.CTkFrame(win)
    btn_frame.pack(pady=10)
    add_buttons(btn_frame, text="Replace", colors_dict=COLORS, command=do_replace).pack(side="left", padx=8)
    add_buttons(btn_frame, text="Cancel", colors_dict=COLORS, command=do_cancel).pack(side="left", padx=8)

    root.wait_window(win)
    return bool(result["replace"])


def confirm_delete(root, site: str, username: str | None) -> bool:
    """Ask user to confirm deletion of a site or a single username entry."""
    win = ctk.CTkToplevel(root)
    win.title("Confirm delete")
    win.geometry("340x160")
    win.transient(root)
    win.grab_set()
    title = create_title(win, "Confirm delete")
    title.pack(pady=8)
    if username:
        create_label(win, f"Delete entry for '{site}' \nwith username '{username}'?").pack(pady=8)
    else:
        create_label(win, f"Delete all entries for site '{site}'?").pack(pady=8)

    result = {"delete": False}

    def do_delete():
        result["delete"] = True
        win.destroy()

    def do_cancel():
        result["delete"] = False
        win.destroy()

    btn_frame = ctk.CTkFrame(win)
    btn_frame.pack(pady=10)
    add_buttons(btn_frame, text="Delete", colors_dict=COLORS, command=do_delete).pack(side="left", padx=8)
    add_buttons(btn_frame, text="Cancel", colors_dict=COLORS, command=do_cancel).pack(side="left", padx=8)

    root.wait_window(win)
    return bool(result["delete"])
