import tkinter as tk
from tkinter import ttk

class CustomButton(tk.Button):

    def __init__(self, master=None, **kw):
        kw.setdefault("bg", "#ffffff")
        kw.setdefault("bg", "#000000")
        kw.setdefault("activebackground", "grey")
        kw.setdefault("relief", "flat")
        kw.setdefault("borderwidth", "0")
        kw.setdefault("font", ("Helvetica", 16))
        kw.setdefault("takefocus", False)

        outlinewidth = kw.pop("outlinewidth", None)
        outlinecolor = kw.pop("outlinecolor", "grey")
        if outlinewidth:
            outline = tk.LabelFrame(master, bd=outlinewidth, bg=outlinecolor, relief=tk.FLAT)
            outline.pack()
            super().__init__(outline, **kw)
        else:
            super().__init__(master, **kw)

        self.bind("<Enter>", self.hover)
        self.bind("<Leave>", self.default)

    def hover(self, event):
        event.widget.configure(font=("Helvetica", 18), bg="lightgrey")

    def default(self, event):
        event.widget.configure(font=("Helvetica", 16), bg="#ffffff")


class CustomToggleButton(CustomButton):

    def __init__(self, master=None, **kw):
        self.state = kw.pop("toggled", False)
        text = kw.pop("text", "")
        self.text_on = kw.pop("text_on", text)
        self.text_off = kw.pop("text_off", text)
        kw["text"] = self.text_off if not self.state else self.text_on
        command = kw.pop("command", self.default_command)
        kw["command"] = lambda: self.toggle(command)
        super().__init__(master, **kw)
    
    def default_command(self):
        pass

    def toggle(self, command):
        self.state = not self.state
        self.config(text=self.text_off if not self.state else self.text_on)
        command()