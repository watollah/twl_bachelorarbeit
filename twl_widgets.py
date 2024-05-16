import tkinter as tk
from tkinter import ttk

class CustomButton(tk.Button):

    def __init__(self, master=None, **kw):
        kw.setdefault("bg", "#ffffff")
        kw.setdefault("activebackground", "grey")
        kw.setdefault("relief", "flat")
        kw.setdefault("borderwidth", "0")
        kw.setdefault("font", ("Helvetica", 16))
        kw.setdefault("takefocus", False)

        outlinewidth = kw.pop("outlinewidth", None)
        outlinecolor = kw.pop("outlinecolor", "grey")
        if outlinewidth:
            outline = tk.LabelFrame(master, bd=outlinewidth, bg=outlinecolor, relief=tk.FLAT)
            outline.pack(fill="x")
            super().__init__(outline, **kw)
        else:
            super().__init__(master, **kw)

        self.bind("<Enter>", self.hover)
        self.bind("<Leave>", self.default)

    def hover(self, event):
        event.widget.configure(bg="lightgrey")

    def default(self, event):
        event.widget.configure(bg="#ffffff")


class CustomToggleButton(CustomButton):

    def __init__(self, master=None, **kw):
        self.state: tk.BooleanVar = kw.pop("variable", tk.BooleanVar())
        text = kw.pop("text", "")
        self.text_on = kw.pop("text_on", text)
        self.text_off = kw.pop("text_off", text)
        kw["text"] = self.text_off if not self.state else self.text_on
        command = kw.pop("command", self.default_command)
        self.state.trace_add("write", lambda *ignore: self.toggle(command))
        kw["command"] = lambda: self.state.set(not self.state.get())
        super().__init__(master, **kw)

    def default_command(self):
        pass

    def toggle(self, command):
        self.config(text=self.text_off if not self.state.get() else self.text_on)
        command()


class ToggledFrame(tk.Frame):

    TABLE_WIDTH: int = 50

    CLOSED_SYMBOL: str = "\u23F5"
    OPEN_SYMBOL: str = "\u23F7"

    def __init__(self, parent, title: str = "", *args, **options):
        tk.Frame.__init__(self, parent, *args, **options)

        self.title: str = title
        self.is_expanded: tk.BooleanVar = tk.BooleanVar(value=True)

        self.title_frame: ttk.Frame = ttk.Frame(self)
        self.title_frame.pack(fill="x")

        self.content: ttk.Frame = ttk.Frame(self)
    
        self.toggle_button = CustomToggleButton(self.title_frame, 
                                                command=lambda: self.content.pack(fill="x") if self.is_expanded.get() else self.content.forget(), 
                                                variable=self.is_expanded, 
                                                text_on=f"{ToggledFrame.OPEN_SYMBOL} {self.title}", 
                                                text_off=f"{ToggledFrame.CLOSED_SYMBOL} {self.title}", 
                                                padx=10, pady=8,
                                                anchor="w",
                                                outlinewidth=1)
        self.toggle_button.pack(fill=tk.BOTH)
        self.is_expanded.set(True)