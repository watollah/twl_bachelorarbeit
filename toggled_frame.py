import tkinter as tk
from tkinter import ttk 


class ToggledFrame(tk.Frame):

    TABLE_WIDTH: int = 50

    CLOSED_SYMBOL: str = "\u25B6"
    OPEN_SYMBOL: str = "\u25BC"

    def __init__(self, parent, title: str = "", *args, **options):
        tk.Frame.__init__(self, parent, *args, **options)
        
        self.title: str = title
        self.is_expanded: tk.BooleanVar = tk.BooleanVar()

        self.title_frame: ttk.Frame = ttk.Frame(self)
        self.title_frame.pack(fill="x", expand=True)

        self.toggle_button = ttk.Checkbutton(self.title_frame, command=self.toggle, variable=self.is_expanded, style='Toolbutton', width=ToggledFrame.TABLE_WIDTH)
        self.toggle_button.pack(fill=tk.BOTH, expand=True)

        self.content: ttk.Frame = ttk.Frame(self, relief="groove", borderwidth=1)
        
        self.toggle()

    def toggle(self):
        if self.is_expanded.get():
            self.content.pack(fill="x", expand=1)
            self.toggle_button.configure(text=f"{ToggledFrame.OPEN_SYMBOL} {self.title}")
        else:
            self.content.forget()
            self.toggle_button.configure(text=f"{ToggledFrame.CLOSED_SYMBOL} {self.title}")