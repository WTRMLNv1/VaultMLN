# add_password.py
# Manages the add password screen class for UI
from customtkinter import CTkFrame, CTkEntry, CENTER
import customtkinter as ctk
from PIL import Image
from ui.popups import empty_fields_alert, password_mismatch_alert, simple_alert, confirm_replace
from ui.helpers import create_title, divider, frame, add_buttons, create_label, get_colors, home_button, DEFAULT_FONT, BASE_DIR
from Functions.manager import store_json, list_sites, delete_site


class AddPasswordScreen:
    def __init__(self, ui):
        self.ui = ui
        self.frame = self.ui.frame
        self.eye_open_img = ctk.CTkImage(dark_image=Image.open(f"{BASE_DIR}/assets/eye_open.png"), size=(20, 20))
        self.colors = get_colors()
        self.accent_color = self.colors["accent_color"]
        self.hover_color = self.colors["hover_color"]
        self.text_color = self.colors["text_color"]
        if self.text_color == "white":
            self.eye_open_img = ctk.CTkImage(light_image=Image.open(f"{BASE_DIR}/assets/eye_open_white.png"), size=(20, 20))
            self.eye_closed_img = ctk.CTkImage(light_image=Image.open(f"{BASE_DIR}/assets/eye_closed_white.png"), size=(20, 20))
        else:
            self.eye_closed_img = ctk.CTkImage(dark_image=Image.open(f"{BASE_DIR}/assets/eye_closed.png"), size=(20, 20))
            self.eye_open_img = ctk.CTkImage(dark_image=Image.open(f"{BASE_DIR}/assets/eye_open.png"), size=(20, 20))
        self.frame.place(relx=0.5, rely=0.5, anchor=CENTER, relwidth=0.9, relheight=0.9)
        self.add_widgets()

    def add_widgets(self):
        self.title = create_title(self.frame, "Add New Password")
        self.title.place(relx=0.5, rely=0.05, anchor=CENTER)

        self.home_button = home_button(self.frame, self.ui, self.accent_color, self.hover_color, self.text_color)

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
        
        self.hide_button = ctk.CTkButton(self.frame, image=self.eye_closed_img, text="", width=30, height=30, fg_color=self.accent_color, hover_color=self.hover_color, cursor="hand2", command=self.toggle_password)
        self.hide_button.place(relx=0.86, rely=0.5, anchor="w")
    
        self.submit_button = add_buttons(self.frame, text="Submit", command=self.add_password, colors_dict=self.colors)
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
            # check for existing username on same site
            sites = list_sites(self.ui.master_password)
            existing = sites.get(site)
            if existing:
                # existing is a list of dicts with 'user' and 'password'
                match = next((e for e in existing if e.get("user") == user), None)
                if match:
                    # ask user whether to replace
                    replace = confirm_replace(self.frame, site, user)
                    if not replace:
                        return
                    # delete only the matching entry
                    deleted = delete_site(site, self.ui.master_password, username=user)
            store_json(site, user, pw, self.ui.master_password)
            self.ui.show_screen("home")
        except Exception as e:
            simple_alert(self.frame, "Error", f"Failed to store password: {e}")

    def toggle_password(self):
        if self.password_entry.cget("show") == "":
            self.password_entry.configure(show="*")
            self.password_confirm_entry.configure(show="*")
            self.hide_button.configure(image=self.eye_closed_img)
        else:
            self.password_entry.configure(show="")
            self.password_confirm_entry.configure(show="")
            self.hide_button.configure(image=self.eye_open_img)
