# add_password.py
# Manages the add password screen class for UI
from customtkinter import CTkFrame, CTkEntry, CENTER
import customtkinter as ctk
from PIL import Image
from ui.popups import empty_fields_alert, password_mismatch_alert
from ui.helpers import create_title, divider, frame, add_buttons, create_label, DEFAULT_FONT, ACCENT_COLOR, HOVER_COLOR, BASE_DIR
from Functions.manager import store_json
import os

class AddPasswordScreen:
    def __init__(self, ui):
        self.ui = ui
        self.frame = self.ui.frame
        self.eye_open_img = ctk.CTkImage(dark_image=Image.open(f"{BASE_DIR}/assets/eye_open.png"), size=(20, 20))
        self.eye_closed_img = ctk.CTkImage(dark_image=Image.open(f"{BASE_DIR}/assets/eye_closed.png"), size=(20, 20))
        self.home_img = ctk.CTkImage(dark_image=Image.open(f"{BASE_DIR}/assets/homebutton.png"))
        self.frame.place(relx=0.5, rely=0.5, anchor=CENTER, relwidth=0.9, relheight=0.9)
        self.add_widgets()

    def add_widgets(self):
        self.title = create_title(self.frame, "Add New Password")
        self.title.place(relx=0.5, rely=0.05, anchor=CENTER)

        self.home_button = ctk.CTkButton(self.frame, image=self.home_img, text="", font=ctk.CTkFont(size=12, family="Cascadia Code"), fg_color=ACCENT_COLOR, hover_color=HOVER_COLOR, corner_radius=20, cursor="hand2", command=lambda: self.ui.show_screen("home"))
        self.home_button.place(relx=0.05, rely=0.05, anchor="w", relwidth=0.1)

        self.divider = divider(self.frame)
        self.divider.place(relx=0.5, rely=0.1, anchor=CENTER)

        self.site_name_label = create_label(self.frame, "Enter site name")
        self.site_name_label.place(relx=0.05, rely=0.15, anchor="w")

        self.site_name_entry = ctk.CTkEntry(self.frame, placeholder_text="Enter the site name", font=DEFAULT_FONT)
        self.site_name_entry.place(relx=0.05, rely=0.2, anchor="w", relwidth=0.8)

        self.username_label = create_label(self.frame, "Enter your username / email")
        self.username_label.place(relx=0.05, rely=0.3, anchor="w")

        self.username_entry = ctk.CTkEntry(self.frame, placeholder_text="Enter username / email", font=DEFAULT_FONT)
        self.username_entry.place(relx=0.05, rely=0.35, anchor="w", relwidth=0.8)

        self.password_label = create_label(self.frame, "Enter your password")
        self.password_label.place(relx=0.05, rely=0.45, anchor="w")
        
        self.password_entry = ctk.CTkEntry(self.frame, placeholder_text="Enter your password", font=DEFAULT_FONT, show="*")
        self.password_entry.place(relx=0.05, rely=0.5, anchor="w", relwidth=0.8)
        
        self.password_confirm_label = create_label(self.frame, "Confirm your password")
        self.password_confirm_label.place(relx=0.05, rely=0.6, anchor="w")

        self.password_confirm_entry = ctk.CTkEntry(self.frame, placeholder_text="Re-enter your password", font=DEFAULT_FONT, show="*")
        self.password_confirm_entry.place(relx=0.05, rely=0.65, anchor="w", relwidth=0.8)
        
        self.hide_button = ctk.CTkButton(self.frame, image=self.eye_closed_img, text="", width=30, height=30, fg_color=ACCENT_COLOR, hover_color=HOVER_COLOR, cursor="hand2", command=self.toggle_password)
        self.hide_button.place(relx=0.86, rely=0.5, anchor="w")
    
        self.submit_button = add_buttons(self.frame, text="Submit", command=self.add_password)
        self.submit_button.place(relx=0.5, rely=0.8, anchor=CENTER, relwidth=0.3)
    def add_password(self):
        site = self.site_name_entry.get().strip()
        user = self.username_entry.get().strip()
        pw = self.password_entry.get().strip()
        pwc = self.password_confirm_entry.get().strip()
        if not site or not user or not pw:
            empty_fields_alert(self.frame)
            return
        if pw != pwc:
            password_mismatch_alert(self.frame)
            return
        try:
            store_json(site, user, pw, self.ui.master_password)
            self.ui.show_screen("home")
        except Exception as e:
            print("Error storing password:", e)
            return

    def toggle_password(self):
        if self.password_entry.cget("show") == "":
            self.password_entry.configure(show="*")
            self.password_confirm_entry.configure(show="*")
            self.hide_button.configure(image=self.eye_closed_img)
        else:
            self.password_entry.configure(show="")
            self.password_confirm_entry.configure(show="")
            self.hide_button.configure(image=self.eye_open_img)
