import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageDraw

TTK_CLAM = "clam"

FONT_TYPE = "Helvetica"
FONT_SIZE = 10
FONT = (FONT_TYPE, FONT_SIZE)
LARGE_FONT_SIZE = 12
LARGE_FONT = (FONT_TYPE, LARGE_FONT_SIZE)

#Colors
ACCENT = ""
LIGHT_ACCENT = ""

DARK_SELECTED = "#0078D7"
SELECTED = "#99d1ff"
LIGHT_SELECTED = "#cce8ff"

WHITE = "#ffffff"
VERY_LIGHT_GRAY = "#e5e5e5"
LIGHT_GRAY = "#cccccc"
GRAY = "#b3b3b3"
DARK_GRAY = "#999999"
VERY_DARK_GRAY = "#7f7f7f"
BLACK = "#000000"

GREEN = "#008000"
RED = "#ff0000"

SCALE_THUMB_SIZE = 22

theme_images = []

def init_style():

    style = ttk.Style()
    style.theme_use(TTK_CLAM)

    #General Styles
    style.configure("TButton", background=WHITE, relief="flat", font=LARGE_FONT)
    style.map("TButton",
              shiftrelief=[('pressed', '!disabled', 2)],
              background=[('pressed', '!disabled', LIGHT_GRAY), ('active', VERY_LIGHT_GRAY)])

    style.configure("TLabel", background=WHITE, foreground=BLACK, font=FONT)

    style.configure("TNotebook", background=GRAY, borderwidth=0, bordercolor=BLACK)
    style.configure("TNotebook.Tab", padding=(20, 10), font=LARGE_FONT, bordercolor=BLACK, foreground=BLACK, background=VERY_LIGHT_GRAY)
    style.map("TNotebook.Tab",
              expand=[("selected","0 0 0 0")],
              padding=[("selected","20 10")], 
              foreground=[("disabled",DARK_GRAY)],
              background=[("selected",WHITE), ("active",LIGHT_GRAY), ("disabled",LIGHT_GRAY)],
              focuscolor=[("selected",WHITE)])

    style.configure("TPanedwindow", background=VERY_LIGHT_GRAY)
    style.configure("Sash", sashthickness=5, gripcount=0)

    style.configure("Toolbutton", background=WHITE, relief="flat")
    style.map("Toolbutton", 
              shiftrelief=[('pressed', '!disabled', 2), ("selected", 2)],
              background=[("selected", SELECTED),("active", VERY_LIGHT_GRAY)])

    style.configure("Treeview", background=WHITE, fieldbackground=WHITE, bordercolor=BLACK, font=FONT)
    style.map("Treeview", 
              background=[("selected", SELECTED)],
              foreground=[("selected", BLACK)])
    style.configure("Heading", background=WHITE, relief="flat")
    style.map("Heading", background=[("selected", WHITE), ("active",VERY_LIGHT_GRAY)])

    #Custom Styles
    style.configure("Diagram.TLabel", foreground="green")
    style.configure("Outer.Border.TFrame", background=BLACK)
    style.configure("Inner.Border.TFrame", background=VERY_LIGHT_GRAY)

    style.configure("Selected.TButton", background=SELECTED, relief="flat", font=LARGE_FONT)
    style.map("Selected.TButton",
              shiftrelief=[('pressed', '!disabled', 2)],
              background=[('pressed', '!disabled', SELECTED), ('active', SELECTED)])

    style.configure("Diagram.TFrame", background="lightgrey")
    style.configure("ControlPanel.TFrame", background=WHITE)
    style.configure("ControlPanel.TLabel", background=WHITE)

    id_normal = create_scale_image(WHITE)
    id_disabled = create_scale_image(LIGHT_GRAY)
    id_pressed = create_scale_image(LIGHT_GRAY)
    id_hover = create_scale_image(VERY_LIGHT_GRAY)
    track_img = ImageTk.PhotoImage(Image.new("RGB", (40, 5), VERY_LIGHT_GRAY))
    id_track = len(theme_images)
    theme_images.append(track_img)
    h_ttkstyle = "Horizontal.TScale"
    h_element = h_ttkstyle.replace('.TS', '.S')
    style.element_create(f'{h_element}.slider', 'image', theme_images[id_normal],
                                ('disabled', theme_images[id_disabled]),
                                ('pressed', theme_images[id_pressed]),
                                ('hover', theme_images[id_hover]))
    style.element_create(f'{h_element}.track', 'image', theme_images[id_track])
    style.layout(h_ttkstyle,
        [(f'{h_element}.focus', {
            "expand": "1",
            "sticky": tk.NSEW,
            "children": [
                (f'{h_element}.track', {"sticky": tk.EW}),
                (f'{h_element}.slider', {"side": tk.LEFT, "sticky": ""})
            ]}
        )]
    )
    style.configure(h_ttkstyle, background=WHITE)

def create_scale_image(color: str) -> int:
    image = Image.new("RGBA", (100, 100))
    draw = ImageDraw.Draw(image)
    draw.ellipse((0, 0, 95, 95), fill=color, outline=BLACK, width=4)
    hover_img = ImageTk.PhotoImage(
        image.resize((SCALE_THUMB_SIZE, SCALE_THUMB_SIZE), Image.Resampling.LANCZOS)
    )
    id = len(theme_images)
    theme_images.append(hover_img)
    return id