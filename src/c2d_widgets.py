import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont

from c2d_update import Observer
from c2d_style import FONT, Colors
from c2d_images import add_png_by_name


class TwlTab(Observer, ttk.Frame):
    """Base class of the applications tabs."""

    ID: str = ""

    def __init__(self, notebook: ttk.Notebook) -> None:
        """Create an instance of TwlTab."""
        ttk.Frame.__init__(self, notebook)


class ToolTip(object):
    """Class that can display a tooltip on top of a widget. Not used in this version of the app but might be used in future versions."""

    DELAY: int = 500
    WIDTH: int = 200
    OFFSET: int = 20

    def __init__(self, widget, text='widget info'):
        """Create an instance of ToolTip."""
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
        self.id = None
        self.tooltip = None

    def enter(self, event=None):
        """Schedule the creation of a tooltip when the user enters the widget with the cursor."""
        self.schedule()

    def leave(self, event=None):
        """Unschedule the creation of a tooltip and hide the tooltip if there is one when the user exits the widget with the cursor."""
        self.unschedule()
        self.hide()

    def schedule(self):
        """Schedule the creation of a tooltip. Tooltip is created after the time specified in Tooltip.DELAY if the cursor doesn't leave the widget."""
        self.unschedule()
        self.id = self.widget.after(self.DELAY, self.show)

    def unschedule(self):
        """Unschedule the creation of a tooltip."""
        if self.id:
            self.widget.after_cancel(self.id)
            self.id = None

    def show(self, event=None):
        """Show the tooltip on top of the widget."""
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + self.OFFSET
        y += self.widget.winfo_rooty() + self.OFFSET

        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry("+%d+%d" % (x, y))

        label = ttk.Label(self.tooltip, text=self.text, style="Tooltip.TLabel")
        label.pack(ipadx=1)

    def hide(self):
        """Destroy the tooltip if it exists."""
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None


class CustomButton(ttk.Button):
    """Custom styled button widget with a solid outline."""

    def __init__(self, master=None, **kw):
        """Create an instance of CustomButton."""
        outlinewidth = kw.pop("outlinewidth", None)
        outlinecolor = kw.pop("outlinecolor", Colors.BLACK)
        kw.setdefault("takefocus", False)
        if outlinewidth:
            outline = tk.LabelFrame(master, bd=outlinewidth, bg=outlinecolor, relief=tk.FLAT)
            outline.pack(fill="x")
            super().__init__(outline, **kw)
        else:
            super().__init__(master, **kw)
        self.bind("<Enter>", self.hover)
        self.bind("<Leave>", self.default)

    def hover(self, event):
        """Override to change style when cursor enters this widget."""
        pass

    def default(self, event):
        """Override to change style when cursor exits this widget."""
        pass


class CustomToggleButton(CustomButton):
    """Custom styled toggle button widget. Supports on/off icon and text."""

    def __init__(self, master=None, **kw):
        """Create an instance of ToggleButton."""
        self.state: tk.BooleanVar = kw.pop("variable", tk.BooleanVar())
        self.state.trace_add("write", lambda *ignore: self.on_toggle(command))

        text = kw.pop("text", "")
        self.text_on = kw.pop("text_on", text)
        self.text_off = kw.pop("text_off", text)
        kw["text"] = self.text_on if self.state.get() else self.text_off

        self.icon_on = kw.pop("icon_on", None)
        self.icon_off = kw.pop("icon_off", None)
        if self.icon_on and self.icon_off:
            kw["image"] = self.icon_on if self.state.get() else self.icon_off
            kw["compound"] = tk.LEFT

        command = kw.pop("command", self.default_command)
        kw["command"] = self.toggle

        super().__init__(master, **kw)

    def toggle(self):
        """Switch the state of the button when it's pressed."""
        self.state.set(not self.state.get())

    def on_toggle(self, command):
        """Code that gets executed when the state of the button changes."""
        self.configure(text=self.text_off if not self.state.get() else self.text_on)
        if self.icon_on and self.icon_off:
            self.configure(image=self.icon_on if self.state.get() else self.icon_off)
        command()

    def default_command(self):
        """Custom defineable function that gets executed when the state of the button changes."""
        pass


class CustomRadioButton(CustomToggleButton):
    """Custom styled radio button widget. Can be used to group multiple CustomToggleButtons as radio buttons."""

    def __init__(self, master=None, **kw):
        """Create an instance of CustomRadioButton."""
        self.variable: tk.Variable = kw.pop("variable", tk.StringVar())
        self.value = kw.pop("value", "")
        self.variable.trace_add("write", lambda *ignore: self.on_radio_toggle())
        super().__init__(master, **kw)
        self.configure(style="Selected.Radio.TButton" if self.state.get() else "Radio.TButton")

    def toggle(self):
        """Switch the state of the button and set the connected variable to this buttons value."""
        super().toggle()
        self.variable.set(self.value)

    def on_toggle(self, command):
        """When this button is toggled, switch the style of this button to reflect the new state."""
        self.configure(style="Selected.Radio.TButton" if self.state.get() else "Radio.TButton")
        return super().on_toggle(command)

    def on_radio_toggle(self):
        """Executed when there is a change to the variable this radio button is connected to, for example by another radio button with the same variable
        or by external code. Changes the state of this button to reflect the changed variable."""
        if not self.state.get() and self.variable.get() == self.value:
            self.state.set(True)
        elif self.state.get() and not self.variable.get() == self.value:
            self.state.set(False)


class BorderFrame(ttk.Frame):
    """Custom widget built from two nested empty frames with a slight padding to create a border."""

    def __init__(self, master=None, **kw):
        """Create an instance of BorderFrame."""
        kw["style"] = "Outer.Border.TFrame"
        super().__init__(master, **kw)
        ttk.Frame(self, style="Inner.Border.TFrame").pack(padx=1, pady=1, fill="both", expand=True)

class ToggledFrame(tk.Frame):
    """Custom widget with CustomToggleButton with a Frame underneath. 
    When the button is toggled the Frame is visible, otherwise it's collapsed.
    Used for the table sections in the UI."""

    HEADER_SIZE = 50

    OPEN_ICON: str = "arrow_open_icon"
    CLOSED_ICON: str = "arrow_closed_icon"

    def __init__(self, parent, title: str = "", *args, **options):
        """Create an instance of ToggledFrame."""
        tk.Frame.__init__(self, parent, *args, **options)

        self.title: str = title
        self.is_expanded: tk.BooleanVar = tk.BooleanVar(value=True)

        self.title_frame: ttk.Frame = ttk.Frame(self)
        self.title_frame.pack(fill="x")

        self.content: ttk.Frame = ttk.Frame(self)

        open_icon = add_png_by_name(self.OPEN_ICON, self.HEADER_SIZE, self.HEADER_SIZE)
        closed_icon = add_png_by_name(self.CLOSED_ICON, self.HEADER_SIZE, self.HEADER_SIZE)

        self.toggle_button = CustomToggleButton(self.title_frame, 
                                                style="ToggledFrame.TButton",
                                                command=lambda: self.content.pack(fill="x") if self.is_expanded.get() else self.content.forget(), 
                                                variable=self.is_expanded, 
                                                icon_on=open_icon,
                                                icon_off=closed_icon,
                                                text=self.title,
                                                padding=(0, 0),
                                                outlinewidth=1)
        self.toggle_button.pack(fill=tk.BOTH)
        self.is_expanded.set(True)


class CustomMenuButton(ttk.OptionMenu):
    """Custom styled dropdown selection button. Used for the speed selection in CremonaControlPanel."""

    ARROW_SIZE = 5

    def __init__(self, parent, *args, **options):
        """Create an instance of CustomMenuButton."""
        outlinewidth = options.pop("outlinewidth", None)
        outlinecolor = options.pop("outlinecolor", Colors.BLACK)
        if outlinewidth:
            outline = tk.LabelFrame(parent, bd=outlinewidth, bg=outlinecolor, relief=tk.FLAT)
            outline.pack(fill="both", expand=True)
            super().__init__(outline, *args, **options)
        else:
            super().__init__(parent, *args, **options)


class CustomEntry(tk.Entry):
    """Custom entry widget that uses a specified filter method to filter inputs. 
    For invalid inputs a warning popup is displayed with the warning returned by the filter method.
    Used all over the UI."""

    POPUP_WIDTH = 70

    def __init__(self, master, validator, **kwargs):
        """Create an instance of CustomEntry."""
        self.popup = None
        self.validator = validator
        self.variable = tk.StringVar()
        kwargs["validate"] = "key"
        kwargs["validatecommand"] = (master.register(self.validate), "%P")
        kwargs["textvariable"] = self.variable
        kwargs.setdefault("justify", tk.CENTER)
        super().__init__(master, **kwargs)
        self['exportselection'] = False #stop selected text from being copied to clipboard

    def validate(self, new_value) -> bool:
        """Executed whenever a new value is entered in the entry. Shows and hides warning popup."""
        validation = self.validator(new_value)
        if validation[0]:
            self.hide_popup()
        else:
            self.show_popup(validation[1])
        return True

    def show_popup(self, message):
        """Show warning popup with the specified message."""
        if self.popup:
            self.popup.destroy()
        x, y, width = self.winfo_rootx(), self.winfo_rooty() + self.winfo_height(), self.winfo_width()

        #add warning sign icon
        message = "\u26A0 " + message

        #create a temporary label to measure the required height
        temp_label = tk.Label(self, text=message, wraplength=self.POPUP_WIDTH)
        temp_label.pack_forget()  # Pack and forget to trigger geometry computation
        req_height = temp_label.winfo_reqheight()

        #create the popup window
        self.popup = tk.Toplevel(self)
        self.popup.geometry(f"{self.POPUP_WIDTH}x{req_height}+{round(x - ((self.POPUP_WIDTH - width) / 2))}+{y - req_height - self.winfo_height()}")
        self.popup.overrideredirect(True)
        self.popup.attributes("-topmost", True)
        #self.popup.attributes('-alpha', 0.6)

        #create the label with the error message and pack it into the popup window
        label = tk.Label(self.popup, text=message, wraplength=self.POPUP_WIDTH)
        label.pack(expand=True, fill="both")

    def hide_popup(self):
        """Hide the warning popup if it exists."""
        if self.popup:
            self.popup.destroy()
            self.popup = None

class ValidationText(tk.Text):
    """Custom expandable text widget that is used for the validation text at the top of DefinitionDiagram."""

    def __init__(self, master, action, **kwargs):
        """Create an instance of ValidationText."""
        super().__init__(master, kwargs)
        self.is_expanded = False
        self.action = action

    def clear(self):
        """Remove all text from the widget."""
        self.config(state=tk.NORMAL)
        self.delete("1.0", tk.END)
        self.config(state=tk.DISABLED, width=0, height=0)

    def text_add(self, text: str, tag: str, color: str):
        """Add text to the widget and style it with the specified color."""
        self.config(state=tk.NORMAL)
        start = self.index("end-1c")
        self.insert(start, text)
        self.tag_add(tag, start, "end-1c")
        self.tag_config(tag, foreground=color)
        self.resize()
        self.config(state=tk.DISABLED)

    def add_button(self):
        """Add the show more/show less button at the end of the text widget."""
        self.config(state=tk.NORMAL)
        text = "show less" if self.is_expanded else "show more"
        start = self.index("end-1c")
        self.insert(tk.END, f"\n{text}")
        self.tag_add("button", start, tk.END)
        self.tag_config("button", foreground=Colors.BLACK, underline=True)
        self.tag_bind("button", "<Button-1>", self.on_action)
        self.tag_bind("button", "<Enter>", lambda event: event.widget.config(cursor="hand2"))
        self.tag_bind("button", "<Leave>", lambda event: event.widget.config(cursor=""))
        self.resize()
        self.config(state=tk.DISABLED)

    def on_action(self, event):
        """Action executed when the show more/show less button is pressed."""
        self.is_expanded = not self.is_expanded
        self.action()

    def resize(self):
        """Resize the widget size to fit exactly with it's content."""
        width = max(tkfont.Font(font=FONT).measure(line) for line in self.get("1.0", tk.END).split("\n"))
        height = len(self.get("1.0", tk.END).split("\n")) - 1
        self.config(width=(width // tkfont.Font(font=FONT).measure("0") + 1), height=height)