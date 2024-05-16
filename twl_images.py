import tkinter as tk
from PIL import Image, ImageTk
from typing import cast, List


image_references: List[tk.PhotoImage] = []

def add_image(path: str, width: int|None=None, height: int|None=None) -> tk.PhotoImage:
    pil_image = Image.open(path)
    if width and height:
        pil_image = pil_image.resize((width, height), Image.Resampling.LANCZOS)
    tk_image = cast(tk.PhotoImage, ImageTk.PhotoImage(pil_image))
    image_references.append(tk_image)
    return tk_image