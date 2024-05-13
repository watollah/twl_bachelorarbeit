from tkinter import filedialog, messagebox
import json

from twl_components import *

def save_project(statical_system: StaticalSystem) -> bool:
    filename = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
    if filename:
        print("Diagram saved to", filename)
        return True
    return False

def open_project(statical_system: StaticalSystem, is_saved: bool):
    if not is_saved:
        ok = messagebox.askokcancel("Warning", "Opening a new project will discard current changes.", default="cancel")
        if not ok:
            return
    filename = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
    if filename:
        #loaded_diagram = load_diagram_from_file(filename)
        print("Diagram loaded from", filename)