# ui/homepage.py
# Manages the homepage class for UI
from customtkinter import CTkFrame, CTkLabel, CENTER
from  ui.helpers import create_label, create_title, add_image, divider, frame, add_buttons,DEFAULT_FONT, FONT_20
from Functions.manager import list_sites
import os

# How to get parent directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))).replace("\\", "/")

class HomeScreen:
    def __init__(self, ui):
        self.ui = ui
        self.frame = self.ui.frame
        self.frame.place(relx=0.5, rely=0.5, anchor=CENTER, relwidth=0.9, relheight=0.9)
        self.num_sites = len(list_sites(self.ui.master_password))
        self.add_widgets()

    def add_widgets(self):
        self.title = create_title(self.frame, "Home")
        self.title.place(relx=0.5, rely=0.05, anchor=CENTER)

        self.divider = divider(self.frame)
        self.divider.place(relx=0.5, rely=0.1, anchor=CENTER)

        self.logoContainer = CTkFrame(master=self.frame, corner_radius=20, width=160, height=160)
        self.logoContainer.place(relx=0.05, rely=0.15, anchor="nw")

        image_path = os.path.join(BASE_DIR,"assets","VaultMLN.png")
        image_label = add_image(self.logoContainer, image_path, size=(150, 150))
        image_label.place(relx=0.5, rely=0.5, anchor=CENTER)

        self.detailsContainer = frame(self.frame)
        self.detailsContainer.place(relx=0.45, rely=0.15, anchor="nw", relwidth=0.5, relheight=0.3)

        self.details_label = create_label(self.detailsContainer, text="Number of sites stored:")
        self.details_label.place(relx=0.5, rely=0.3, anchor = CENTER)
        self.details_number = create_title(self.detailsContainer, text=self.num_sites)
        self.details_number.place(relx=0.5, rely=0.5, anchor=CENTER)
        self.details_sitesText = create_label(self.detailsContainer, text="sites")
        self.details_sitesText.place(relx=0.5, rely=0.7, anchor=CENTER)

        self.add_passwordsButton = add_buttons(self.frame, text="Add New Password", command=lambda:self.ui.show_screen("add_password"))
        self.add_passwordsButton.place(relx=0.05, rely=0.55, relwidth=0.4)

        self.vaultSettingsButton = add_buttons(self.frame, text="Vault Settings", command=self.ui.show_vault_settings)
        self.vaultSettingsButton.place(relx=0.55, rely=0.55, relwidth=0.4)

        self.checkPasswordButton = add_buttons(self.frame, text="Check Password", command=lambda: self.ui.show_screen("check_passwords"))
        self.checkPasswordButton.place(relx=0.05, rely=0.65, relwidth=0.4)