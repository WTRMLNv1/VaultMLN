# ui/checkSite.py
# Manages the check site screen class for UI
from customtkinter import CTkFrame, CTkEntry, CENTER
import customtkinter as ctk
from PIL import Image
from ui.helpers import create_label, create_title, add_buttons, divider, frame, ACCENT_COLOR, HOVER_COLOR, BASE_DIR, DEFAULT_FONT
from Functions.manager import list_sites, get_data
from ui.popups import simple_alert
import threading

class siteCheckScreen:
    def __init__(self, ui):
        self.ui = ui
        self.pass_visible = False
        self.frame = self.ui.frame
        self.eye_open_img = ctk.CTkImage(dark_image=Image.open(f"{BASE_DIR}/assets/eye_open.png"), size=(20, 20))
        self.eye_closed_img = ctk.CTkImage(dark_image=Image.open(f"{BASE_DIR}/assets/eye_closed.png"), size=(20, 20))
        self.home_img = ctk.CTkImage(dark_image=Image.open(f"{BASE_DIR}/assets/homebutton.png"))
        self.clipboard_img = ctk.CTkImage(dark_image=Image.open(f"{BASE_DIR}/assets/clipboard.png"))
        self.tick_img = ctk.CTkImage(dark_image=Image.open(f"{BASE_DIR}/assets/tick_mark.png"))
        self.frame.place(relx=0.5, rely=0.5, anchor = CENTER, relwidth=0.9, relheight=0.9)
        if list_sites(self.ui.master_password) == {}:
            self.site_names = ["No sites found"]
        else:
            self.site_names = list(list_sites(self.ui.master_password).keys())
        self.add_widgets()

    def add_widgets(self):
        self.title = create_title(self.frame, "View Passwords")
        self.title.place(relx=0.5, rely=0.05, anchor=CENTER)

        self.divider = divider(self.frame)
        self.divider.place(relx=0.5, rely=0.1, anchor=CENTER)

        self.home_button = ctk.CTkButton(self.frame, image=self.home_img, text="", font=ctk.CTkFont(size=12, family="Cascadia Code"), fg_color=ACCENT_COLOR, hover_color=HOVER_COLOR, corner_radius=20, cursor="hand2", command=lambda: self.ui.show_screen("home"))
        self.home_button.place(relx=0.05, rely=0.05, anchor="w", relwidth=0.1)

        self.site_name_label = create_label(self.frame, "Choose site name")
        self.site_name_label.place(relx=0.05, rely=0.15, anchor="w")

        self.site_name_chooser = ctk.CTkOptionMenu(self.frame, values=self.site_names, font=DEFAULT_FONT, fg_color="#343638", button_color="#565B5E", button_hover_color="#393A3B", dropdown_fg_color="#393939", dropdown_hover_color="#787878", text_color="white")
        self.site_name_chooser.place(relx=0.05, rely=0.2, anchor="w", relwidth=0.8)
    
        self.get_data_button = add_buttons(self.frame, text="Get Data", command=self.check_site)
        self.get_data_button.place(relx=0.5, rely=0.3, anchor=CENTER, relwidth=0.3)

        self.data_frame = frame(self.frame)
        self.data_frame.place(relwidth=0.8, relheight=0.3, relx=0.5, rely=0.7, anchor=CENTER)

        self.user_label = create_label(self.data_frame, "username / email:")
        self.user_label.place(relx=0.5, rely=0.3, anchor=CENTER)
        self.password_label = create_label(self.data_frame, "password:")
        self.password_label.place(relx=0.5, rely=0.5, anchor=CENTER)

    def toggle_password(self):
        if self.pass_visible:
            char_count = len(self.password)
            self.password_label.configure(text=f"password: {'*' * char_count}")
            self.hide_button.configure(image=self.eye_closed_img)
        else:
            self.password_label.configure(text=f"password: {self.password}")
            self.hide_button.configure(image=self.eye_open_img)
        self.pass_visible = not self.pass_visible
    
    def copy_to_clipboard(self):
        self.ui.root.clipboard_clear()
        self.ui.root.clipboard_append(self.password)
        self.ui.root.update()
        self.copy_button.configure(image=self.tick_img)
        threading.Timer(1.0, self.reset_clipboard_button).start()
        
    def reset_clipboard_button(self):
        self.copy_button.configure(image=self.clipboard_img)
        

    def check_site(self):
        selected_site = self.site_name_chooser.get()
        site_data = get_data(selected_site, self.ui.master_password)

        if not site_data["ok"]:
            simple_alert(self.frame, "Error", f"Error {site_data['code']}: {site_data['message']}")
            return
        
        self.user = site_data["user"]
        self.password = site_data["password"]

        self.user_label.configure(text=f"username / email: {self.user}")
        self.password_label.configure(text="password: " + "*" * len(self.password))

        self.copy_button = ctk.CTkButton(self.data_frame, image=self.clipboard_img, text="", font=ctk.CTkFont(size=12, family="Cascadia Code"), fg_color=ACCENT_COLOR, hover_color=HOVER_COLOR, corner_radius=20, cursor="hand2", command=self.copy_to_clipboard)
        self.copy_button.place(relx=0.4, rely=0.7, anchor=CENTER, relwidth=0.15)

        self.hide_button = ctk.CTkButton(self.data_frame, image=self.eye_closed_img, text="", width=30, height=30, fg_color=ACCENT_COLOR, hover_color=HOVER_COLOR, cursor="hand2", corner_radius=20, command=self.toggle_password)
        self.hide_button.place(relx=0.6, rely=0.7, anchor=CENTER, relwidth=0.15)


        