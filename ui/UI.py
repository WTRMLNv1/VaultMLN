# ui/UI.py
# Creates the main UI.
import customtkinter as ctk
from ui.homepage import HomeScreen
from ui.add_password import AddPasswordScreen
from ui.enterPassword import EnterPasswordScreen
from ui.popups import tell_unlock_required
from ui.checkSite import siteCheckScreen
from ui.settingsScreen import SettingsScreen
from ui.deletePassword import deletePasswordScreen
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
        elif screen_name == "settings":
            SettingsScreen(self)
        elif screen_name == "delete_password":
            deletePasswordScreen(self)
        else:
            ctk.CTkLabel(
                self.frame, text=f"Unknown screen: {screen_name}"
            ).place(relx=0.5, rely=0.5, anchor="center")
