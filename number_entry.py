import tkinter as tk

class NumberEntry(tk.Entry):

    def __init__(self, master, **kwargs):
        self.popup = None
        self.lower_limit = kwargs.pop('lower_limit', 0)
        self.upper_limit = kwargs.pop('upper_limit', float('inf'))
        kwargs["validate"] = "key"
        kwargs["validatecommand"] = (master.register(self.validate), "%P")
        super().__init__(master, **kwargs)

    def validate(self, new_value):
        if not new_value:
            self.hide_popup()
            return True
        try:
            num = float(new_value)
            if self.lower_limit <= num <= self.upper_limit:
                self.hide_popup()
                return True
            else:
                self.show_popup(f"Value must be between {self.lower_limit} and {self.upper_limit}")
                return False
        except ValueError:
            self.show_popup("Invalid input")
            return False
    
    def show_popup(self, message):
        if self.popup:
            self.popup.destroy()
        x, y, width = self.winfo_rootx(), self.winfo_rooty() + self.winfo_height(), self.winfo_width()
        
        # Create a temporary label to measure the required height
        temp_label = tk.Label(self, text=message, wraplength=width)
        temp_label.pack_forget()  # Pack and forget to trigger geometry computation
        req_height = temp_label.winfo_reqheight()
        
        # Create the popup window
        self.popup = tk.Toplevel(self)
        self.popup.geometry(f"{width}x{req_height}+{x}+{y}")
        self.popup.overrideredirect(True)
        self.popup.attributes('-alpha', 0.6)
        
        # Create the label with the error message and pack it into the popup window
        label = tk.Label(self.popup, text=message, wraplength=width)
        label.pack(expand=True, fill="both")

    def hide_popup(self):
        if self.popup:
            self.popup.destroy()
            self.popup = None
