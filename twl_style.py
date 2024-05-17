from tkinter import ttk

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

WHITE = "white"
VERY_LIGHT_GRAY = "gray90"
LIGHT_GRAY = "gray80"
GRAY = "gray70"
DARK_GRAY = "gray60"
VERY_DARK_GRAY = "gray50"
BLACK = "black"

GREEN = "green"
RED = "red"

def init_style():

    style = ttk.Style()
    style.theme_use("clam")

    #General Styles
    style.configure("TButton", background="red")

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

    style.configure("Toolbutton", background=WHITE, relief="flat", shiftrelief=0, bordercolor=BLACK)
    style.map("Toolbutton", 
              shiftrelief=[("selected", 1)],
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
    style.configure("Inner.Border.TFrame", background=LIGHT_GRAY)

    style.configure("Diagram.TFrame", background="lightgrey")
    style.configure("ControlPanel.TFrame", background=WHITE)
    style.configure("ControlPanel.TLabel", background=WHITE)
    style.configure("TScale", background=WHITE)