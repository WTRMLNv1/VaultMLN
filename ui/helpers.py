# ui/helpers.py
# Helper functions for UI components
# from json import load, dump, JSONDecodeError
from doctest import master
import os
from customtkinter import CTkLabel, CTkButton, CTkImage, CTkFrame, CTkFont, CENTER
from PIL import Image
from Functions.colorPicker import darker, ideal_text_color
from Functions.themeManager import get_theme, set_theme


DEFAULT_FONT = ("Cascadia Code", 14)
FONT_20 = ("Cascadia Code", 20)
ACCENT_COLOR = "#8B5CF6"
HOVER_COLOR = "#6F49C4"
FONT_COLOR = "#FFFFFF"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))).replace("\\", "/")
HOME_IMG = CTkImage(dark_image=Image.open(f"{BASE_DIR}/assets/homebutton.png"))
HOME_IMG_LIGHT = CTkImage(light_image=Image.open(f"{BASE_DIR}/assets/homebutton_white.png"))
EYE_OPEN_IMG = CTkImage(dark_image=Image.open(f"{BASE_DIR}/assets/eye_open.png"), size=(20, 20))
EYE_CLOSED_IMG = CTkImage(dark_image=Image.open(f"{BASE_DIR}/assets/eye_closed.png"), size=(20, 20))
EYE_OPEN_IMG_LIGHT = CTkImage(light_image=Image.open(f"{BASE_DIR}/assets/eye_open_white.png"), size=(20, 20))
EYE_CLOSED_IMG_LIGHT = CTkImage(light_image=Image.open(f"{BASE_DIR}/assets/eye_closed_white.png"), size=(20, 20))
# ========= WIDGET HELPER FUNCTIONS ========== 
def create_label(master: object, text:str, text_color="white" , size:int=14,font_family:str="Cascadia Code", image:object=None) -> object:
    """Creates a label with the text, font, color, and image provided on the parent provided

    Args:
        master (object): The parent to put the label on.
        text (str): The text of the Label
        text_color (str, optional): The color of the text. Defaults to "white".
        size (int, optional): The size of the text. Defaults to 14.
        font_family (str, optional): The font of the text. Defaults to "Cascadia Code.
        image (object, optional): The image to add to the text. Defaults to None.

    Returns:
        object: A CTKLabel object
    """
    return CTkLabel(master=master, text=text,text_color=text_color ,image=image, font=(font_family, size))

def add_image(root: object, path:str, size:tuple=(100, 100)) -> object:
    """Creates a CTkLabel with the image whose path is provided of the size provided

    Args:
        root (object): The root CTk object or CTkFrame object to add the label on to
        path (str): The path of the image to add
        size (tuple, optional): The size of the image. Defaults to (100, 100).

    Returns:
        object: A CTkLabel object with the image provided 
    """
    image = CTkImage(dark_image=Image.open(path), size=size)
    return create_label(root, "", image=image)

def _add_buttons(master: object, text: str, image_path:str=None, command=None, text_color:str="White", fg_color:str=ACCENT_COLOR, hover_color:str=HOVER_COLOR) -> object:
    """Creates a CTkButton with the specified arguements
    Legacy Function. No longer in use

    Args:
        master (object): master to put the button on
        text (str): Text to put in the button
        command (_type_, optional): What the button should do when clicked. Defaults to None.
        text_color (str, optional): Text color. Defaults to "White".
        fg_color (str, optional): Hex Code for the color of the button, defaults to #8B5CF6
        hover_color (str, optional) Hex code for the color of the button while hovering on it. Defaults to #6F49C4 
    Returns:
        object: A CTkButton object
    """
    return CTkButton(master=master, text=text, command=command, font=DEFAULT_FONT, text_color=text_color, fg_color=fg_color, hover_color=hover_color, corner_radius=20)

def add_buttons(master: object, text: str, colors_dict: dict = None, command=None, fg_color: str = None, hover_color: str = None, text_color: str = None) -> CTkButton:
    """Creates a CTkButton using either `colors_dict` or provided color kwargs.

    Accepts either:
    - `colors_dict` as returned by `get_colors()` with keys `accent_color`, `hover_color`, `text_color`
    - or explicit `fg_color`, `hover_color`, `text_color` kwargs
    Backwards compatible with older callers that pass `fg_color` by keyword.
    """
    # Resolve colors priority: explicit kwargs > colors_dict > defaults
    final_fg = None
    final_hover = None
    final_text = None
    if isinstance(colors_dict, dict):
        final_fg = colors_dict.get("accent_color") or colors_dict.get("accent")
        final_hover = colors_dict.get("hover_color")
        final_text = colors_dict.get("text_color")
    # override with explicit kwargs if provided
    if fg_color:
        final_fg = fg_color
    if hover_color:
        final_hover = hover_color
    if text_color:
        final_text = text_color
    # fallbacks
    if not final_fg:
        final_fg = ACCENT_COLOR
    if not final_hover:
        try:
            final_hover = darker(final_fg)
        except Exception:
            final_hover = HOVER_COLOR
    if not final_text:
        final_text = ideal_text_color(final_fg)

    return CTkButton(master=master, text=text, command=command, font=DEFAULT_FONT, text_color=final_text, fg_color=final_fg, hover_color=final_hover, corner_radius=20)


def create_title(master: object, text:str, text_color:str = "white") -> CTkLabel:
    """Creates a title label with the text anc color provided

    Args:
        master (object): The parent to put the label on.
        text (str): The text of the Label
        text_color (str, optional): The color of the text (defaults to white)

    Returns:
        object: A CTKLabel object
    """
    return CTkLabel(master=master, text=text, text_color=text_color, font=("Cascadia Code", 20, "bold"))

def divider(master):
    return CTkFrame(master, height=2, fg_color="gray30")

def frame(master, corner_radius:int=20):
    return CTkFrame(master=master, corner_radius=corner_radius)

def home_button(master, ui, accent_color=ACCENT_COLOR, hover_color=HOVER_COLOR, text_color="black"):
    if text_color == "black":
        home_button = CTkButton(master, image=HOME_IMG, text="", font=CTkFont(size=12, family="Cascadia Code"), fg_color=accent_color, hover_color=hover_color, corner_radius=20, cursor="hand2", command=lambda: ui.show_screen("home"))
    elif text_color == "white":
        home_button = CTkButton(master, image=HOME_IMG_LIGHT, text="", font=CTkFont(size=12, family="Cascadia Code"), fg_color=accent_color, hover_color=hover_color, corner_radius=20, cursor="hand2", command=lambda: ui.show_screen("home"))
    else:
        return None
    home_button.place(relx=0.05, rely=0.05, anchor="w", relwidth=0.1)

def get_colors() -> dict:
    """
    Returns the accent color, hover color, and text color (black or white) 
    to be used in the GUI.
    
    Returns:
    color_dict (Dict): {"accent_color": str, "hover_color": str, "text_color": str} Contains the accent color, hover color, and text color.
    """ 
    accent_color = get_theme()
    hover_color = darker(accent_color)
    text_color = ideal_text_color(accent_color)
    return {"accent_color": accent_color, "hover_color": hover_color, "text_color": text_color}
    
# ========= Testing area ========= #
if __name__ == "__main__":
    None

