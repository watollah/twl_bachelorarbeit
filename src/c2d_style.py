import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageDraw, ImageFont

from c2d_images import add_image


TTK_CLAM = "clam" #ttk style that this application's style is build on

FONT_TYPE = "Helvetica"

FONT_SIZE = 10
FONT = (FONT_TYPE, FONT_SIZE)

LARGE_FONT_SIZE = 12
LARGE_FONT = (FONT_TYPE, LARGE_FONT_SIZE)

VERY_LARGE_FONT_SIZE = 20
VERY_LARGE_FONT = (FONT_TYPE, VERY_LARGE_FONT_SIZE)

SCALE_THUMB_SIZE = 22

CHECK_SIZE = 18
CHECK_SYMBOL = "✔"


class Colors:
    """Class that stores all color values used throughout the ui."""

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
    LIGHT_RED = "#ffcccc"


def init_style():
    """Initialize and register the Styles for all UI widgets."""
    style = ttk.Style()
    style.theme_use(TTK_CLAM)

    #General Styles
    style.configure("TButton", background=Colors.WHITE, relief="flat", font=LARGE_FONT)
    style.map("TButton",
              shiftrelief=[('pressed', '!disabled', 2)],
              background=[('pressed', '!disabled', Colors.LIGHT_GRAY), ('active', Colors.VERY_LIGHT_GRAY)])

    style.configure("ToggledFrame.TButton", anchor=tk.W)
    style.configure("Play.TButton", font=VERY_LARGE_FONT, padding=(4, -6, 0, 0))

    style.configure("TLabel", background=Colors.WHITE, foreground=Colors.BLACK, font=FONT)

    style.configure("TNotebook", background=Colors.GRAY, borderwidth=0, bordercolor=Colors.BLACK)
    style.configure("TNotebook.Tab", padding=(20, 10), font=LARGE_FONT, bordercolor=Colors.BLACK, foreground=Colors.BLACK, background=Colors.VERY_LIGHT_GRAY)
    style.map("TNotebook.Tab",
              expand=[("selected","0 0 0 0")],
              padding=[("selected","20 10")], 
              foreground=[("disabled",Colors.DARK_GRAY)],
              background=[("selected",Colors.WHITE), ("active",Colors.LIGHT_GRAY), ("disabled",Colors.LIGHT_GRAY)],
              focuscolor=[("selected",Colors.WHITE)])

    style.configure("TPanedwindow", background=Colors.VERY_LIGHT_GRAY)
    style.configure("Sash", sashthickness=5, gripcount=0)

    style.configure("Toolbutton", background=Colors.WHITE, relief="flat")
    style.map("Toolbutton", 
              shiftrelief=[('pressed', '!disabled', 2), ("selected", 2)],
              background=[("selected", Colors.SELECTED),("active", Colors.VERY_LIGHT_GRAY)])

    style.configure("Treeview", background=Colors.WHITE, fieldbackground=Colors.WHITE, bordercolor=Colors.BLACK, font=FONT)
    style.map("Treeview", 
              background=[("selected", Colors.SELECTED)],
              foreground=[("selected", Colors.BLACK)])
    style.configure("Heading", background=Colors.WHITE, relief="flat")
    style.map("Heading", background=[("selected", Colors.WHITE), ("active",Colors.VERY_LIGHT_GRAY)])

    #Custom Styles
    style.configure("Diagram.TLabel", foreground="green")
    style.configure("Outer.Border.TFrame", background=Colors.BLACK)
    style.configure("Inner.Border.TFrame", background=Colors.VERY_LIGHT_GRAY)

    style.configure("Radio.TButton", padding=(0, 0))
    style.configure("Selected.Radio.TButton", background=Colors.SELECTED, relief="flat", font=LARGE_FONT)
    style.map("Selected.Radio.TButton",
              shiftrelief=[('pressed', '!disabled', 2)],
              background=[('pressed', '!disabled', Colors.SELECTED), ('active', Colors.SELECTED)])

    style.configure("Diagram.TFrame", background="lightgrey")
    style.configure("ControlPanel.TFrame", background=Colors.WHITE)
    style.configure("ControlPanel.TLabel", background=Colors.WHITE)

    normal_img = create_scale_image(Colors.WHITE)
    disabled_img = create_scale_image(Colors.LIGHT_GRAY)
    pressed_img = create_scale_image(Colors.LIGHT_GRAY)
    hover_img = create_scale_image(Colors.VERY_LIGHT_GRAY)
    track_img = add_image(Image.new("RGB", (40, 5), Colors.VERY_LIGHT_GRAY))
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
    style.configure(h_ttkstyle, background=Colors.WHITE)

    cb_ttk_style = "Custom.TCheckbutton"
    cb_element = cb_ttk_style.replace(".TC", ".C")
    cb_off_image = create_checkbutton_image(Colors.BLACK, "")
    cb_on_image = create_checkbutton_image(Colors.BLACK, CHECK_SYMBOL)
    cb_disabled_image = create_checkbutton_image(Colors.GRAY, "")
    style.element_create(f'{cb_element}.indicator', 'image', cb_on_image,
                                  ('disabled', cb_disabled_image),
                                  ('!selected', cb_off_image),
                                  width=CHECK_SIZE + 5, border=2, sticky=tk.W)
    style.configure(cb_ttk_style, foreground=Colors.BLACK, background=Colors.WHITE, takefocus="false")
    style.map(cb_ttk_style, foreground=[('disabled', Colors.GRAY)], background=[("active", Colors.VERY_LIGHT_GRAY)])
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

    style.configure("TMenubutton", background=Colors.WHITE, relief="flat", font=FONT)
    style.map("TMenubutton", background=[('pressed', '!disabled', Colors.LIGHT_GRAY), ('active', Colors.VERY_LIGHT_GRAY)])

def create_scale_image(color: str) -> tk.PhotoImage:
    """Create a round slider button for the control panel slider. The default one looks very outdated."""
    image = Image.new("RGBA", (100, 100))
    draw = ImageDraw.Draw(image)
    draw.ellipse((0, 0, 95, 95), fill=color, outline=Colors.BLACK, width=4)
    return add_image(image, SCALE_THUMB_SIZE, SCALE_THUMB_SIZE)

def create_checkbutton_image(color: str, text: str) -> tk.PhotoImage:
    """Create the checkmark image for checkbuttons in the UI."""
    checkbutton_on = Image.new("RGBA", (134, 134))
    draw = ImageDraw.Draw(checkbutton_on)
    draw.rectangle([2, 2, 132, 132], outline=color, width=6, fill=Colors.WHITE)
    fnt = ImageFont.truetype("seguisym.ttf", 110)
    draw.text((20, -10), text, font=fnt, fill=Colors.BLACK)
    return add_image(checkbutton_on, CHECK_SIZE, CHECK_SIZE)