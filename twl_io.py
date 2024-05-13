from tkinter import filedialog, messagebox
import json

from twl_components import *

def clear_project(statical_system: StaticalSystem, is_saved: bool):
    if not statical_system.is_empty() and not is_saved:
        ok = messagebox.askokcancel("Warning", "Creating a new project will discard current changes.", default="cancel")
        if not ok:
            return
    statical_system.clear()
    print("Project cleared")

def save_project(statical_system: StaticalSystem) -> bool:
    filename = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
    if filename:
        print("Project saved to", filename)
        return True
    return False

def open_project(statical_system: StaticalSystem, is_saved: bool):
    if not is_saved:
        ok = messagebox.askokcancel("Warning", "Opening a new project will discard current changes.", default="cancel")
        if not ok:
            return
    filename = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
    if filename:
        statical_system.clear()
        print("Project loaded from", filename)