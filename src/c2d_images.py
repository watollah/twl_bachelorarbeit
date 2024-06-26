import os
import sys
import tkinter as tk
from PIL import Image, ImageTk
from typing import cast


image_references: list[tk.PhotoImage] = []

def add_image(pil_image: Image.Image, width: int|None=None, height: int|None=None) -> tk.PhotoImage:
    if width and height:
        pil_image = pil_image.resize((width, height), Image.Resampling.LANCZOS)
    tk_image = cast(tk.PhotoImage, ImageTk.PhotoImage(pil_image))
    image_references.append(tk_image)
    return tk_image

def add_image_by_name(name: str, width: int|None=None, height: int|None=None) -> tk.PhotoImage:
    pil_image = Image.open(get_image_path(name))
    return add_image(pil_image, width, height)

def get_image_path(image_name: str):
    """Get absolute path to resource, works for dev and for PyInstaller."""
    try:
        #PyInstaller creates a temporary folder and stores path in _MEIPASS
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    except AttributeError:
        base_path = os.path.abspath(".")
    img_dir = os.path.join(base_path, '..', 'img')
    return os.path.join(img_dir, f"{image_name}.png")