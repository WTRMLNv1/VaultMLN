# settingsScreen.py
# Manages the settings screen of the UI
import customtkinter as ctk
from Functions.colorPicker import hex_to_hsv, hex_to_rgb, hsv_to_hex, darker, ideal_text_color
from customtkinter import CENTER
from ui.popups import simple_alert, success_alert
from ui.helpers import create_label, create_title, add_buttons, divider, home_button, get_colors
from Functions.themeManager import get_theme, set_theme
from ui.vaultSettings import change_master_password, wipe_all_passwords

class CTkColorPicker(ctk.CTkFrame):
    """UI-only color picker that uses helper converters from Functions/colorPicker."""
    def __init__(self, master, initial_color="#8B5CF6", hover_factor=0.8, **kwargs):
        super().__init__(master, **kwargs)
        self.hover_factor = hover_factor
        self.font = ctk.CTkFont(size=12, family="Cascadia Code")

        self.preview = ctk.CTkFrame(self, width=120, height=80, corner_radius=12, fg_color=initial_color)
        self.preview.pack(padx=10, pady=(6, 10))

        ctk.CTkLabel(self, text="Hue", font=self.font).pack(anchor="w", padx=8)
        self.hue = ctk.CTkSlider(self, from_=0, to=360, command=lambda _=None: self._update_color())
        self.hue.pack(fill="x", padx=8, pady=(0, 6))

        ctk.CTkLabel(self, text="Saturation", font=self.font).pack(anchor="w", padx=8)
        self.sat = ctk.CTkSlider(self, from_=0, to=100, command=lambda _=None: self._update_color())
        self.sat.pack(fill="x", padx=8, pady=(0, 6))

        ctk.CTkLabel(self, text="Value", font=self.font).pack(anchor="w", padx=8)
        self.val = ctk.CTkSlider(self, from_=0, to=100, command=lambda _=None: self._update_color())
        self.val.pack(fill="x", padx=8, pady=(0, 6))

        self._set_from_hex(initial_color)
        self._update_color()

    def _set_from_hex(self, hex_color):
        if hex_to_hsv:
            h, s, v = hex_to_hsv(hex_color)
            self.hue.set(h)
            self.sat.set(s)
            self.val.set(v)

    def _update_color(self):
        if hsv_to_hex:
            h = self.hue.get()
            s = self.sat.get()
            v = self.val.get()
            self.fg_color = hsv_to_hex(h, s, v)
            if darker:
                self.hover_color = darker(self.fg_color, self.hover_factor)
            else:
                self.hover_color = self.fg_color
            self.preview.configure(fg_color=self.fg_color)

    def get_selected_color(self):
        return getattr(self, 'fg_color', '#8B5CF6'), getattr(self, 'hover_color', '#6946BD')

class SettingsScreen:
    def __init__(self, ui):
        self.ui = ui
        self.frame = self.ui.frame
        self.frame.place(relx=0.5, rely=0.5, anchor=CENTER, relwidth=0.9, relheight=0.9)
        self.colors = get_colors()
        self.accent_color = self.colors['accent_color']
        self.hover_color = self.colors['hover_color']
        self.text_color = self.colors['text_color']
        self.red_colors = {'accent_color': "#b62828", 'hover_color': darker("#b62828"), 'text_color': ideal_text_color("#b62828")}
        self.add_widgets()

    def set_colors(self):
        try:
            accent, hover = self.color_picker.get_selected_color()
            set_theme(accent_color=accent)
            success_alert(self.frame,"Accent color updated successfully!")
        except Exception as e:
            simple_alert(self.frame, "Error", str(e))

    def default_accent_color(self):
        try:
            default = "#8B5CF6"
            # reset UI picker sliders and preview if present
            if hasattr(self, 'color_picker') and self.color_picker is not None:
                try:
                    self.color_picker._set_from_hex(default)
                    self.color_picker._update_color()
                except Exception:
                    pass
            set_theme(accent_color=default)
            success_alert(self.frame, "Accent color reset to default")
        except Exception as e:
            simple_alert(self.frame, "Error", str(e))

    def add_widgets(self):
        self.title = create_title(self.frame, text="Settings")
        self.title.place(relx=0.5, rely=0.05, anchor=CENTER)

        divider(self.frame).place(relx=0.5, rely=0.08, anchor=CENTER)

        home_button(self.frame, self.ui, accent_color=self.accent_color, hover_color=self.hover_color, text_color=self.text_color)
        try:
            initial_accent = self.colors['accent_color']
        except Exception:
            initial_accent = "#8B5CF6"
        
        self.accent_label = create_label(self.frame, "Accent Color:")
        self.accent_label.place(relx=0.05, rely=0.15, anchor="w")

        self.color_picker = CTkColorPicker(self.frame, initial_accent, height=210)
        self.color_picker.place(relx=0.05, rely=0.18, relwidth=0.9)

        self.save_accent_button = add_buttons(self.frame, "Set Accent Color", colors_dict=self.colors, command=self.set_colors)
        self.save_accent_button.place(relx=0.05, rely=0.69, relwidth=0.4, anchor="w")

        self.reset_to_defaults_button = add_buttons(self.frame, "Reset to Default", colors_dict=self.colors, command=self.default_accent_color)
        self.reset_to_defaults_button.place(relx=0.55, rely=0.69, relwidth=0.4, anchor="w")

        # Vault Settings

        self.vault_settings_title = create_title(self.frame, "Danger Zone", text_color="red")
        self.vault_settings_title.place(relx=0.5, rely=0.77, anchor=CENTER)

        divider(self.frame).place(relx=0.5, rely=0.8, anchor=CENTER)

        self.change_pw_button = add_buttons(self.frame, text="Change Password", colors_dict=self.colors, command=lambda: change_master_password(self.frame, self.ui.master_password))
        self.change_pw_button.place(relx=0.05, rely=0.83, relwidth=0.4)

        self.wipe_pw_button = add_buttons(self.frame, text="Wipe all Passwords", colors_dict=self.red_colors, command=lambda: wipe_all_passwords(self.frame, self.ui.master_password))
        self.wipe_pw_button.place(relx=0.55, rely=0.83, relwidth=0.4)