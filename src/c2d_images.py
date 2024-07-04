import os
import sys
import tkinter as tk
from PIL import Image, ImageTk
from typing import cast


image_references: list[tk.PhotoImage] = []

def add_image(pil_image: Image.Image, width: int|None=None, height: int|None=None) -> tk.PhotoImage:
    """Add an image to the application. Resizes it to the specified width and height and stores a reference to keep it in memory."""
    if width and height:
        pil_image = pil_image.resize((width, height), Image.Resampling.LANCZOS)
    tk_image = cast(tk.PhotoImage, ImageTk.PhotoImage(pil_image))
    image_references.append(tk_image)
    return tk_image

def add_png_by_name(name: str, width: int|None=None, height: int|None=None) -> tk.PhotoImage:
    """Add a png by specifying it's name. The image is looked up in the img folder."""
    pil_image = Image.open(get_image_path(name, "png"))
    return add_image(pil_image, width, height)

def get_image_path(image_name: str, image_type: str):
    """Get absolute path to image, works for dev and for PyInstaller."""
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__))) #PyInstaller creates a temporary folder and stores path in _MEIPASS
    if base_path.endswith("src"):
        base_path = os.path.join(base_path, '..')
    return os.path.join(base_path, 'img', f"{image_name}.{image_type}")