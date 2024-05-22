import tkinter as tk
from tkinter import ttk

def tk_color_to_hex(root, color_name):
    try:
        # Use winfo_rgb to get the RGB values
        r, g, b = root.winfo_rgb(color_name)
        
        # Convert 16-bit values (0-65535) to 8-bit values (0-255)
        r = r // 256
        g = g // 256
        b = b // 256
        
        # Format as hex string
        hex_color = f'#{r:02x}{g:02x}{b:02x}'
        return hex_color
    except tk.TclError:
        return None

def convert_color(event=None):
    color_name = entry.get()
    hex_color = tk_color_to_hex(root, color_name)
    result_text.config(state=tk.NORMAL)
    result_text.delete("1.0", tk.END)
    if hex_color:
        result_text.insert(tk.END, hex_color)
        result_text.config(background=color_name)
        tk_label.config(background=color_name)
        hex_label.config(background=color_name)
        root.config(background=color_name)
    else:
        result_text.insert(tk.END, "Invalid color name")
        result_text.config(background="white")
        tk_label.config(background="white")
        hex_label.config(background="white")
        root.config(background="white")
    result_text.config(state=tk.DISABLED)

# Create the main Tkinter root window
root = tk.Tk()
root.title("Color Converter")

# Set the window to always stay on top
root.attributes("-topmost", True)

# Fix the window size
root.geometry("250x120")
root.resizable(False, False)

tk_label = ttk.Label(root, text="Tk Color:")
tk_label.pack(pady=(5,0))

entry = ttk.Entry(root, width=30)
entry.pack(fill="x", expand=True, padx=20)
entry.bind('<KeyRelease>', convert_color)
entry.focus_set()

hex_label = ttk.Label(root, text="Hex Color:")
hex_label.pack()

result_text = tk.Text(root, height=1, state=tk.DISABLED, wrap=tk.WORD, background="white")
result_text.pack(fill="x", expand=True, padx=20, pady=(0,10))

root.mainloop()
