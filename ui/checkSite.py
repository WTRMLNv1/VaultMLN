# ui/checkSite.py
# Manages the check site screen class for UI
from customtkinter import CTkFrame, CTkEntry, CENTER
import customtkinter as ctk
from PIL import Image
from ui.helpers import create_label, create_title, add_buttons, divider, frame, get_colors, home_button, BASE_DIR, DEFAULT_FONT, HOME_IMG, EYE_OPEN_IMG, EYE_CLOSED_IMG, EYE_CLOSED_IMG_LIGHT, EYE_OPEN_IMG_LIGHT
from Functions.manager import list_sites, list_site_names, get_data, get_site_display_names
from ui.popups import simple_alert
import threading

class SiteSearchWidget(CTkFrame):
    """Search bar with an always-open scrollable list of CTkButton items.

    - Calls `list_site_names()` once and keeps it in `self.all_sites`.
    - Filters locally on <KeyRelease> and rebuilds the list of buttons.
    - Calls `callback(site_name)` when a site button is clicked.
    """
    def __init__(self, master, all_sites, callback, **kwargs):
        super().__init__(master, **kwargs)
        self.btn_list = []
        # `all_sites` is a list of items: {"label","site","username"}
        self.all_sites = list(all_sites) if all_sites else []
        self.callback = callback
        self.site_widgets = []
        self.selected = None
        self.search_var = ctk.StringVar()
        self.entry = CTkEntry(self, textvariable=self.search_var, font=DEFAULT_FONT, placeholder_text="Search sites...")
        self.entry.pack(fill="x", padx=6, pady=(6, 4))
        self.entry.bind("<KeyRelease>", self._on_keyrelease)
        self.scroll = ctk.CTkScrollableFrame(self)
        self.scroll.pack(fill="both", expand=True, padx=6, pady=(0,6))
        # initial build
        self.rebuild_list(self.all_sites)

    def _on_keyrelease(self, event):
        try:
            text = self.search_var.get().lower()
            if text == "":
                filtered = list(self.all_sites)
            else:
                filtered = [item for item in self.all_sites if text in (item.get("label") or "").lower()]
            if not filtered:
                filtered = [{"label": "No sites found", "site": None, "username": None}]
            self.rebuild_list(filtered)
        except Exception:
            # avoid crashing UI from unexpected input
            self.rebuild_list([{"label": "No sites found", "site": None, "username": None}])

    def rebuild_list(self, items):
        # destroy old widgets
        self.btn_list.clear()
        for w in self.site_widgets:
            try:
                w.destroy()
            except Exception:
                pass
        self.site_widgets.clear()
        # build new buttons
        for item in items:
            label = item.get("label") if isinstance(item, dict) else str(item)
            btn = ctk.CTkButton(self.scroll, text=label, anchor="w", fg_color="#3A3A3A", hover_color="#5C5C5C", font=DEFAULT_FONT, cursor="hand2")
            # attach metadata to button
            btn.site = item.get("site") if isinstance(item, dict) else None
            btn.username = item.get("username") if isinstance(item, dict) else None

            btn.configure(command=lambda b=btn: self._on_click(b))
            self.btn_list.append(btn)
            btn.pack(fill="x", pady=2, padx=2)
            self.site_widgets.append(btn)
    def _on_click(self, button):
        # new signature: pass button
        for btn in self.btn_list:
            btn.configure(fg_color="#3A3A3A", hover_color="#5C5C5C")
        # ignore placeholder
        if button.cget("text") == "No sites found":
            return
        self.selected = button
        button.configure(fg_color="#123456")
        button.configure(hover_color="#22486E")
        self.search_var.set(button.cget("text"))
        try:
            if callable(self.callback):
                self.callback(button)
        except Exception:
            # swallow errors from callback to keep UI responsive
            pass

class siteCheckScreen:
    def __init__(self, ui):
        self.ui = ui
        self.pass_visible = False
        self.frame = self.ui.frame
        self.colors = get_colors()
        self.hover_color = self.colors['hover_color']
        self.accent_color = self.colors['accent_color']
        self.text_color = self.colors['text_color']
        if self.text_color == "white":
            self.eye_open_img = EYE_OPEN_IMG_LIGHT
            self.eye_closed_img = EYE_CLOSED_IMG_LIGHT
            self.clipboard_img = ctk.CTkImage(light_image=Image.open(f"{BASE_DIR}/assets/clipboard_white.png"))
            self.tick_img = ctk.CTkImage(light_image=Image.open(f"{BASE_DIR}/assets/tick_mark_white.png"))
        else:
            self.eye_open_img = EYE_OPEN_IMG
            self.eye_closed_img = EYE_CLOSED_IMG
            self.clipboard_img = ctk.CTkImage(dark_image=Image.open(f"{BASE_DIR}/assets/clipboard.png"))
            self.tick_img = ctk.CTkImage(dark_image=Image.open(f"{BASE_DIR}/assets/tick_mark.png"))
        self.frame.place(relx=0.5, rely=0.5, anchor = CENTER, relwidth=0.9, relheight=0.9)
        # load site names once and keep in memory while typing
        self.sites_resp = get_site_display_names(self.ui.master_password)
        if self.sites_resp.get("ok"):
            self.site_items = self.sites_resp.get("items", [])
        else:
            self.site_items = []
        if not self.site_items:
            self.site_items = [{"label": "No sites found", "site": None, "username": None}]
        self.site_names = list(self.site_items)
        self.selected_site = None
        self.selected_username = None
        self.add_widgets()

    def add_widgets(self):
        self.title = create_title(self.frame, "View Passwords")
        self.title.place(relx=0.5, rely=0.05, anchor=CENTER)

        self.divider = divider(self.frame)
        self.divider.place(relx=0.5, rely=0.1, anchor=CENTER)

        self.homebutton = home_button(self.frame, self.ui, accent_color=self.accent_color, hover_color=self.hover_color, text_color=self.text_color)

        self.site_name_label = create_label(self.frame, "Choose site name")
        self.site_name_label.place(relx=0.05, rely=0.15, anchor="w")

        # Search widget: entry on top, scrollable list of CTkButton items below
        self.search_widget = SiteSearchWidget(self.frame, all_sites=self.site_names, callback=self.on_site_selected)
        self.search_widget.place(relx=0.5, rely=0.33, anchor=CENTER, relwidth=0.8, relheight=0.25)
    
        self.get_data_button = add_buttons(self.frame, text="Get Data", command=self.check_site, colors_dict=self.colors)
        self.get_data_button.place(relx=0.5, rely=0.5, anchor=CENTER, relwidth=0.3)

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
        selected_site = self.selected_site
        if not selected_site:
            simple_alert(self.frame, "No selection", "Please select a site from the list first.")
            return
        site_data = get_data(selected_site, self.ui.master_password)
        if not site_data or not site_data.get("ok"):
            code = site_data.get('code') if isinstance(site_data, dict) else '??'
            message = site_data.get('message') if isinstance(site_data, dict) else 'Unknown error'
            simple_alert(self.frame, "Error", f"Error {code}: {message}")
            return
        entries = site_data["user"]

        if getattr(self, "selected_username", None):
            entry = next((e for e in entries if e["user"] == self.selected_username), None)
            if entry is None:
                entry = entries[0]
        else:
            entry = entries[0]

        self.user = entry["user"]
        self.password = entry["password"]

        self.user_label.configure(text=f"username / email: {self.user}")
        self.password_label.configure(text="password: " + "*" * len(self.password))

        self.copy_button = ctk.CTkButton(self.data_frame, image=self.clipboard_img, text="", font=ctk.CTkFont(size=12, family="Cascadia Code"), fg_color=self.accent_color, hover_color=self.hover_color, corner_radius=20, cursor="hand2", command=self.copy_to_clipboard)
        self.copy_button.place(relx=0.4, rely=0.7, anchor=CENTER, relwidth=0.15)

        self.hide_button = ctk.CTkButton(self.data_frame, image=self.eye_closed_img, text="", width=30, height=30, fg_color=self.accent_color, hover_color=self.hover_color, cursor="hand2", corner_radius=20, command=self.toggle_password)
        self.hide_button.place(relx=0.6, rely=0.7, anchor=CENTER, relwidth=0.15)

    def on_site_selected(self, button):
        """Called by the search widget when a site is clicked."""
        try:
            if not button:
                return
            self.selected_site = button.site
            self.selected_username = button.username
        except Exception:
            # keep UI stable if callback misbehaves
            self.selected_site = None
            self.selected_username = None


        