# Functions/colorPicker.py
# This script provides functions to manipulate colors, specifically to create darker variants of given colors.
import colorsys

def hex_to_hsv(hex_color: str):
    """Convert #RRGGBB to HSV (h in degrees, s and v as percentages)."""
    # Defensive input validation
    if isinstance(hex_color, dict) and "accent" in hex_color:
        hex_color = hex_color["accent"]
    if not isinstance(hex_color, str):
        raise TypeError(f"hex_color must be a string like '#RRGGBB', got {type(hex_color).__name__}")
    if not hex_color.startswith("#") or len(hex_color) != 7:
        raise ValueError(f"Invalid hex color format: {hex_color!r}. Expected '#RRGGBB'.")
    r = int(hex_color[1:3], 16) / 255.0
    g = int(hex_color[3:5], 16) / 255.0
    b = int(hex_color[5:7], 16) / 255.0
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    return h * 360.0, s * 100.0, v * 100.0

def hsv_to_hex(h_deg: float, s_perc: float, v_perc: float) -> str:
    """Convert HSV (h in degrees, s/v in percent) to #RRGGBB."""
    h = float(h_deg) / 360.0
    s = float(s_perc) / 100.0
    v = float(v_perc) / 100.0
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return "#{:02X}{:02X}{:02X}".format(int(r * 255), int(g * 255), int(b * 255))

def darker(hex_color: str, factor: float = 0.8) -> str:
    """Return a darker variant of the provided hex color by scaling Value."""
    h, s, v = hex_to_hsv(hex_color)
    v = max(0.0, min(100.0, v * factor))
    return hsv_to_hex(h, s, v)

def hex_to_rgb(hex_color: str) -> tuple:
    """Convert #RRGGBB to (R, G, B) tuple."""
    if isinstance(hex_color, dict) and "accent" in hex_color:
        hex_color = hex_color["accent"]
    if not isinstance(hex_color, str) or not hex_color.startswith("#") or len(hex_color) != 7:
        raise ValueError(f"Invalid hex color format: {hex_color!r}. Expected '#RRGGBB'.")
    r = int(hex_color[1:3], 16)
    g = int(hex_color[3:5], 16)
    b = int(hex_color[5:7], 16)
    return (r, g, b)

def ideal_text_color(bg_hex):
    r, g, b = hex_to_rgb(bg_hex)
    luminance = (0.299*r + 0.587*g + 0.114*b)
    return "black" if luminance > 186 else "white"

