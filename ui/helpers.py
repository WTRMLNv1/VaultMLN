# ui/helpers.py
# Helper functions for UI components
# from json import load, dump, JSONDecodeError

from customtkinter import CTkLabel, CTkButton, CTkImage, CTkFrame, CENTER
from PIL import Image
import os

DEFAULT_FONT = ("Cascadia Code", 14)
FONT_20 = ("Cascadia Code", 20)
ACCENT_COLOR = "#8B5CF6"
HOVER_COLOR = "#6F49C4"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))).replace("\\", "/")


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

def add_buttons(master: object, text: str, image_path:str=None, command=None, text_color:str="White", fg_color:str=ACCENT_COLOR, hover_color:str=HOVER_COLOR) -> object:
    """Creates a CTkButton with the specified arguements

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

def create_title(master: object, text:str):
    """Creates a title label with the text provided

    Args:
        master (object): The parent to put the label on.
        text (str): The text of the Label

    Returns:
        object: A CTKLabel object
    """
    return CTkLabel(master=master, text=text, text_color="white", font=("Cascadia Code", 20, "bold"))

def divider(master):
    return CTkFrame(master, height=2, fg_color="gray30")

def frame(master, corner_radius:int=20):
    return CTkFrame(master=master, corner_radius=corner_radius)

# ========= Testing area ========= #
if __name__ == "__main__":
    None

