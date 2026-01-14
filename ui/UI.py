# ui/UI.py
# Creates the main UI.
import customtkinter as ctk
from ui.homepage import HomeScreen
from ui.add_password import AddPasswordScreen
from ui.enterPassword import EnterPasswordScreen
from ui.vaultSettings import open_vault_settings
from ui.popups import tell_unlock_required
from ui.checkSite import siteCheckScreen
from customtkinter import CENTER
import os
import ctypes

class UI:
    def __init__(self):
        # === Setup === #
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")        
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("VaultMLN")
        self.root = ctk.CTk()
        self.root.title("VaultMLN")
        self.root.minsize(500, 600)
        self.root.resizable(False, False)

        # Try to set icon safely
        try:
            ico_path = os.path.join("assets", "VaultMLN-no-text.ico")
            if os.path.exists(ico_path):
                self.root.iconbitmap(ico_path)
        except Exception:
            pass

        # Content frame (full screen, swappable area)
        self.frame = ctk.CTkFrame(self.root, corner_radius=20)

        # master password stored only in memory for this session
        self.master_password = None

        # default to password entry screen on startup
        self.show_screen("enter_password")

        self.root.mainloop()
    
    def show_vault_settings(self):
        if not self.master_password:
            tell_unlock_required(self.root)
            return
        open_vault_settings(self.root, self.master_password)

    def show_screen(self, screen_name: str):
        # Clear content frame only
        for widget in self.frame.winfo_children():
            widget.destroy()

        if screen_name == "home":
            HomeScreen(self)
        elif screen_name == "enter_password":
            EnterPasswordScreen(self)
        elif screen_name == "add_password":
            AddPasswordScreen(self)
        elif screen_name == "check_passwords":
            siteCheckScreen(self)
        else:
            ctk.CTkLabel(
                self.frame, text=f"Unknown screen: {screen_name}"
            ).place(relx=0.5, rely=0.5, anchor="center")

    def _prompt_master_password(self):
        """Modal prompt to ask for the master password. Empty = use legacy key."""
        win = ctk.CTkToplevel(self.root)
        win.title("Enter Master Password")
        win.geometry("400x150")
        win.transient(self.root)
        win.grab_set()

        label = ctk.CTkLabel(win, text="Enter master password (leave empty to use file key)")
        label.pack(pady=(20, 8))
        entry = ctk.CTkEntry(win, show="*", width=300)
        entry.pack(pady=(0, 12))

        def submit():
            self.master_password = entry.get() or None
            win.grab_release()
            win.destroy()

        submit_btn = ctk.CTkButton(win, text="Submit", command=submit)
        submit_btn.pack()
        self.root.wait_window(win)
