import customtkinter as ctk
from ui.helpers import add_buttons, create_label, create_title
from customtkinter import CENTER

def simple_alert(root, title: str, message: str):
    win = ctk.CTkToplevel(root)
    win.title(title)
    win.geometry("300x200")
    win.transient(root)
    win.grab_set()
    title = create_title(win, title)
    title.pack(pady=8)
    create_label(win, message).pack(pady=12)
    add_buttons(win, text="OK", command=win.destroy).pack(pady=6)
    root.wait_window(win)

def tell_unlock_required(root):
    simple_alert(root, "Unlock Required", "Please unlock the vault to \naccess settings.")

def empty_fields_alert(root):
    simple_alert(root, "Empty fields", "Empty fields detected. Please \nfill out all fields and try again.")

def password_mismatch_alert(root):
    simple_alert(root, "Passwords dont match", "The passwords entered do not match. \n Please try again.")

def success_alert(root, message: str):
    simple_alert(root, "Success", message)
