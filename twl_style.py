import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageDraw, ImageFont

from twl_images import *

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

CHECK_SIZE = 18
CHECK_SYMBOL = "✔"

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

    normal_img = create_scale_image(WHITE)
    disabled_img = create_scale_image(LIGHT_GRAY)
    pressed_img = create_scale_image(LIGHT_GRAY)
    hover_img = create_scale_image(VERY_LIGHT_GRAY)
    track_img = add_image(Image.new("RGB", (40, 5), VERY_LIGHT_GRAY))
    h_ttkstyle = "Horizontal.TScale"
    h_element = h_ttkstyle.replace('.TS', '.S')
    style.element_create(f'{h_element}.slider', 'image', normal_img,
                                ('disabled', disabled_img),
                                ('pressed', pressed_img),
                                ('hover', hover_img))
    style.element_create(f'{h_element}.track', 'image', track_img)
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

    cb_ttk_style = "Custom.TCheckbutton"
    cb_element = cb_ttk_style.replace(".TC", ".C")
    cb_off_image = create_checkbutton_image(BLACK, "")
    cb_on_image = create_checkbutton_image(BLACK, CHECK_SYMBOL)
    cb_disabled_image = create_checkbutton_image(GRAY, "")
    style.element_create(f'{cb_element}.indicator', 'image', cb_on_image,
                                  ('disabled', cb_disabled_image),
                                  ('!selected', cb_off_image),
                                  width=CHECK_SIZE + 5, border=2, sticky=tk.W)
    style.configure(cb_ttk_style, foreground=BLACK, background=WHITE, takefocus="false")
    style.map(cb_ttk_style, foreground=[('disabled', GRAY)], background=[("active", VERY_LIGHT_GRAY)])
    style.layout(cb_ttk_style,
        [("Checkbutton.padding", {
            "children": [(f'{cb_element}.indicator', {
                "side": tk.LEFT, "sticky": ""
                }), ("Checkbutton.focus", {
                    "children": [
                    ("Checkbutton.label", {"sticky": tk.NSEW})], 
                    "side": tk.LEFT, "sticky": ""
                })
            ], "sticky": tk.NSEW
        })]
    )

    style.configure("TMenubutton", background=WHITE, relief="flat", font=FONT)
    style.map("TMenubutton", background=[('pressed', '!disabled', LIGHT_GRAY), ('active', VERY_LIGHT_GRAY)])

def create_scale_image(color: str) -> tk.PhotoImage:
    image = Image.new("RGBA", (100, 100))
    draw = ImageDraw.Draw(image)
    draw.ellipse((0, 0, 95, 95), fill=color, outline=BLACK, width=4)
    return add_image(image, SCALE_THUMB_SIZE, SCALE_THUMB_SIZE)

def create_checkbutton_image(color: str, text: str) -> tk.PhotoImage:
        checkbutton_on = Image.new("RGBA", (134, 134))
        draw = ImageDraw.Draw(checkbutton_on)
        draw.rectangle(
            [2, 2, 132, 132],
            outline=color,
            width=6,
            fill=WHITE,
        )
        fnt = ImageFont.truetype("seguisym.ttf", 110)
        draw.text((20, -10), text, font=fnt, fill=BLACK)
        return add_image(checkbutton_on, CHECK_SIZE, CHECK_SIZE)