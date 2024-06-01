import tkinter as tk
from tkinter import ttk

from twl_style import *


class ToolTip(object):

    DELAY: int = 500
    WIDTH: int = 200
    OFFSET: int = 20

    """Create a tooltip for a given widget."""
    def __init__(self, widget, text='widget info'):
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
        self.id = None
        self.tooltip = None

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hide()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.DELAY, self.show)

    def unschedule(self):
        if self.id:
            self.widget.after_cancel(self.id)
            self.id = None

    def show(self, event=None):
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + self.OFFSET
        y += self.widget.winfo_rooty() + self.OFFSET

        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry("+%d+%d" % (x, y))

        label = ttk.Label(self.tooltip, text=self.text, style="Tooltip.TLabel")
        label.pack(ipadx=1)

    def hide(self):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None


class CustomButton(ttk.Button):

    def __init__(self, master=None, **kw):
        outlinewidth = kw.pop("outlinewidth", None)
        outlinecolor = kw.pop("outlinecolor", BLACK)
        anchor = kw.pop("anchor", tk.CENTER)
        kw.setdefault("takefocus", False)
        if outlinewidth:
            outline = tk.LabelFrame(master, bd=outlinewidth, bg=outlinecolor, relief=tk.FLAT)
            outline.pack(fill="x")
            super().__init__(outline, **kw)
        else:
            super().__init__(master, **kw)
        ttk.Style().configure(self.winfo_class(), anchor=anchor)
        self.bind("<Enter>", self.hover)
        self.bind("<Leave>", self.default)

    def hover(self, event):
        pass

    def default(self, event):
        pass


class CustomToggleButton(CustomButton):

    def __init__(self, master=None, **kw):
        self.state: tk.BooleanVar = kw.pop("variable", tk.BooleanVar())
        self.state.trace_add("write", lambda *ignore: self.on_toggle(command))

        text = kw.pop("text", "")
        self.text_on = kw.pop("text_on", text)
        self.text_off = kw.pop("text_off", text)
        kw["text"] = self.text_off if not self.state.get() else self.text_on

        command = kw.pop("command", self.default_command)
        kw["command"] = self.toggle

        super().__init__(master, **kw)

    def toggle(self):
        """Switch the state of the button when it's pressed."""
        self.state.set(not self.state.get())

    def on_toggle(self, command):
        """Code that gets executed when the state of the button changes."""
        self.config(text=self.text_off if not self.state.get() else self.text_on)
        command()

    def default_command(self):
        """Custom defineable function that gets executed when the state of the button changes."""
        pass


class CustomRadioButton(CustomToggleButton):

    def __init__(self, master=None, **kw):
        self.variable: tk.Variable = kw.pop("variable", tk.StringVar())
        self.value = kw.pop("value", "")
        self.variable.trace_add("write", lambda *ignore: self.on_radio_toggle())
        super().__init__(master, **kw)

    def toggle(self):
        super().toggle()
        self.variable.set(self.value)

    def on_toggle(self, command):
        self.configure(style="Selected.TButton" if self.state.get() else "TButton")
        return super().on_toggle(command)

    def on_radio_toggle(self):
        if not self.state.get() and self.variable.get() == self.value:
            self.state.set(True)
        elif self.state.get() and not self.variable.get() == self.value:
            self.state.set(False)


class ToggledFrame(tk.Frame):

    TABLE_WIDTH: int = 50

    CLOSED_SYMBOL: str = "\u25B6"
    OPEN_SYMBOL: str = "\u25BC"

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
                                                text_on=f"{ToggledFrame.OPEN_SYMBOL}    {self.title}", 
                                                text_off=f"{ToggledFrame.CLOSED_SYMBOL}    {self.title}", 
                                                padding=(18, 16),
                                                anchor=tk.W,
                                                outlinewidth=1)
        self.toggle_button.pack(fill=tk.BOTH)
        self.is_expanded.set(True)


class CustomMenuButton(ttk.OptionMenu):

    ARROW_SIZE = 5

    def __init__(self, parent, *args, **options):
        outlinewidth = options.pop("outlinewidth", None)
        outlinecolor = options.pop("outlinecolor", BLACK)
        if outlinewidth:
            outline = tk.LabelFrame(parent, bd=outlinewidth, bg=outlinecolor, relief=tk.FLAT)
            outline.pack(fill="both", expand=True)
            super().__init__(outline, *args, **options)
        else:
            super().__init__(parent, *args, **options)


class CustomEntry(tk.Entry):

    def __init__(self, master, validator, **kwargs):
        self.popup = None
        self.validator = validator
        kwargs["validate"] = "key"
        kwargs["validatecommand"] = (master.register(self.validate), "%P")
        kwargs["justify"] = tk.CENTER
        super().__init__(master, **kwargs)
        self['exportselection'] = False #stop selected text from being copied to clipboard

    def validate(self, new_value) -> bool:
        validation = self.validator(new_value)
        if validation[0]:
            self.hide_popup()
        else:
            self.show_popup(validation[1])
        return True

    def show_popup(self, message):
        if self.popup:
            self.popup.destroy()
        x, y, width = self.winfo_rootx(), self.winfo_rooty() + self.winfo_height(), self.winfo_width()

        #add warning sign icon
        message = "\u26A0 " + message

        #create a temporary label to measure the required height
        temp_label = tk.Label(self, text=message, wraplength=width)
        temp_label.pack_forget()  # Pack and forget to trigger geometry computation
        req_height = temp_label.winfo_reqheight()

        #create the popup window
        self.popup = tk.Toplevel(self)
        self.popup.geometry(f"{width}x{req_height}+{x}+{y - req_height - self.winfo_height()}")
        self.popup.overrideredirect(True)
        #self.popup.attributes('-alpha', 0.6)

        #create the label with the error message and pack it into the popup window
        label = tk.Label(self.popup, text=message, wraplength=width)
        label.pack(expand=True, fill="both")

    def hide_popup(self):
        if self.popup:
            self.popup.destroy()
            self.popup = None