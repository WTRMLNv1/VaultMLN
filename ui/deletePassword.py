# ui/deletePassword.py
# This module provides a UI for deleting password entries.
from customtkinter import CENTER
import customtkinter as ctk
from ui.popups import simple_alert, confirm_delete
from ui.helpers import create_label, create_title, divider, add_buttons, get_colors, home_button, frame, DEFAULT_FONT
from Functions.manager import delete_site, get_site_display_names
from ui.checkSite import SiteSearchWidget


class deletePasswordScreen:
    def __init__(self, ui):
        self.ui = ui
        self.frame = self.ui.frame
        self.colors = get_colors()
        self.accent_color = self.colors['accent_color']
        self.hover_color = self.colors['hover_color']
        self.text_color = self.colors['text_color']
        self.site_items = []
        self.selected_site = None
        self.selected_username = None
        self.add_widgets()

    def add_widgets(self):
        self.title = create_title(self.frame, "Delete Passwords")
        self.title.place(relx=0.5, rely=0.05, anchor=CENTER)

        self.home_button = home_button(self.frame, self.ui, accent_color=self.accent_color, hover_color=self.hover_color, text_color=self.text_color)

        self.divider = divider(self.frame)
        self.divider.place(relx=0.5, rely=0.1, anchor=CENTER)

        resp = get_site_display_names(self.ui.master_password)
        if resp.get("ok"):
            self.site_items = resp.get("items", [])
        else:
            self.site_items = [{"label": "No sites found", "site": None, "username": None}]

        self.search_widget = SiteSearchWidget(self.frame, all_sites=self.site_items, callback=self.on_item_selected)
        self.search_widget.place(relx=0.5, rely=0.33, anchor=CENTER, relwidth=0.8, relheight=0.25)

        self.delete_button = add_buttons(self.frame, text="Delete Selected", colors_dict=self.colors, command=self.confirm_and_delete)
        self.delete_button.place(relx=0.5, rely=0.5, anchor=CENTER, relwidth=0.4)

        self.status_label = create_label(self.frame, "No selection", text_color=self.text_color, size=14)
        self.status_label.place(relx=0.5, rely=0.65, anchor=CENTER)

    def refresh_list(self):
        resp = get_site_display_names(self.ui.master_password)
        if resp.get("ok"):
            self.site_items = resp.get("items", [])
        else:
            self.site_items = [{"label": "No sites found", "site": None, "username": None}]
        self.search_widget.rebuild_list(self.site_items)

    def on_item_selected(self, button):
        try:
            if not button:
                return
            self.selected_site = button.site
            self.selected_username = button.username
            label = button.cget("text")
            self.status_label.configure(text=f"Selected: {label}")
        except Exception:
            self.selected_site = None
            self.selected_username = None
            self.status_label.configure(text="No selection")

    def confirm_and_delete(self):
        if not self.selected_site:
            simple_alert(self.frame, "No selection", "Please select a site to delete.")
            return

        confirmed = confirm_delete(self.frame, self.selected_site, self.selected_username)
        if not confirmed:
            return

        try:
            deleted = delete_site(self.selected_site, self.ui.master_password, username=self.selected_username)
            if deleted:
                simple_alert(self.frame, "Deleted", "Entry deleted successfully.")
                self.selected_site = None
                self.selected_username = None
                self.status_label.configure(text="No selection")
                self.refresh_list()
            else:
                simple_alert(self.frame, "Not found", "No matching entry was found to delete.")
        except Exception as e:
            simple_alert(self.frame, "Error", f"Failed to delete: {e}")

