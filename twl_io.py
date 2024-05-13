from tkinter import filedialog, messagebox
import json

from twl_components import *

def save_project(statical_system: StaticalSystem) -> bool:
    filename = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
    if filename:
        print("Diagram saved to", filename)
        return True
    return False

def open_project(statical_system: StaticalSystem):
    response = messagebox.askyesnocancel("Warning", "Opening a new project will discard current changes. Do you want to save first?")
    if response:  # If user chooses to save
        save_project(statical_system)
    elif response is False:  # If user chooses to discard
        filename = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if filename:
            #loaded_diagram = load_diagram_from_file(filename)
            print("Diagram loaded from", filename)