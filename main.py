import tkinter as tk
import ttkbootstrap as ttk
import webbrowser

from twl_toggled_frame import *
from twl_diagram import *
from twl_table import *
from twl_ui import *

def tab_changed(event):
    print("Tab changed!")

def main():
    root = ttk.Window()
    root.geometry("1200x800")
    root.title("TWL Tool")

    statical_system = StaticalSystem()

    create_menu_bar(root)

    style = ttk.Style()
    style.configure('TNotebook.Tab', padding=(20, 10), font=("Helvetica", 12))

    notebook = ttk.Notebook(root)

    definition_tab = ttk.Frame(notebook)
    result_tab = ttk.Frame(notebook)
    profiles_tab = ttk.Frame(notebook)

    notebook.add(definition_tab, text="Definition")
    notebook.add(CremonaTab(notebook, statical_system), text="Cremona")
    notebook.add(result_tab, text="Result")
    notebook.add(profiles_tab, text="(Profiles)")

    label3 = tk.Label(result_tab, text="Results")
    label3.pack(padx=10, pady=10)

    label4 = tk.Label(profiles_tab, text="Profiles (maybe added later)")
    label4.pack(padx=10, pady=10)

    notebook.bind("<<NotebookTabChanged>>", tab_changed)
    notebook.pack(fill=tk.BOTH, expand=True)

    paned_window = ttk.PanedWindow(definition_tab, orient=ttk.HORIZONTAL)
    paned_window.pack(fill=tk.BOTH, expand=True)

    #Diagram Editor
    editor_frame = ttk.Frame(paned_window)
    editor_frame.pack_propagate(False)
    paned_window.add(editor_frame, weight=3)

    diagram = TwlDiagram(editor_frame, statical_system)
    diagram.pack(fill="both", expand=True)

    statical_system.widgets.append(diagram)
    
    #Tables
    menu_frame = ttk.Frame(paned_window)
    menu_frame.pack_propagate(False)
    paned_window.add(menu_frame, weight=1)

    beams_entry = ToggledFrame(menu_frame, "Beams")
    beams_entry.pack(fill="x")
    add_table(beams_entry.content, statical_system.beams)
    
    supports_entry = ToggledFrame(menu_frame, "Supports")
    supports_entry.pack(fill="x")
    add_table(supports_entry.content, statical_system.supports)

    forces_entry = ToggledFrame(menu_frame, "Forces")
    forces_entry.pack(fill="x")
    add_table(forces_entry.content, statical_system.forces)
    
    root.mainloop()

def create_menu_bar(root: tk.Tk):
    # Create a menu bar
    menubar = tk.Menu(root)

    # Create File menu
    file_menu = tk.Menu(menubar, tearoff=0)
    file_menu.add_command(label="Open", command=lambda: print("Not implemented yet."))
    file_menu.add_separator()
    file_menu.add_command(label="Save", command=lambda: print("Not implemented yet."))
    file_menu.add_command(label="Save As...", command=lambda: print("Not implemented yet."))
    menubar.add_cascade(label="File", menu=file_menu)

    # Create Settings menu
    settings_menu = tk.Menu(menubar, tearoff=0)
    show_node_labels = tk.BooleanVar()
    settings_menu.add_checkbutton(label="Show Node Labels", variable=show_node_labels, command=lambda: print("Not implemented yet."))
    show_beam_labels = tk.BooleanVar()
    settings_menu.add_checkbutton(label="Show Beam Labels", variable=show_beam_labels, command=lambda: print("Not implemented yet."))
    show_force_labels = tk.BooleanVar()
    settings_menu.add_checkbutton(label="Show Force Labels", variable=show_force_labels, command=lambda: print("Not implemented yet."))
    show_support_labels = tk.BooleanVar()
    settings_menu.add_checkbutton(label="Show Support Labels", variable=show_support_labels, command=lambda: print("Not implemented yet."))
    menubar.add_cascade(label="Settings", menu=settings_menu)

    # Create Help menu and link to 
    help_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_command(label="Help", command=lambda: webbrowser.open("https://example.com"))

    # Configure the root window to use the menu bar
    root.config(menu=menubar)

def add_table(menu_frame: ttk.Frame, component_list: ComponentList) -> TwlTable:
    table = TwlTable(menu_frame, component_list)
    component_list.statical_system.widgets.append(table)
    columns: tuple = component_list.component_class.attribute_names
    column_indices: tuple = tuple(f"#{i}" for i in range(1, len(columns) + 1))
    table.configure(columns=column_indices)
    table.heading("#0", text="Id")
    for i in range(0, len(columns)): table.heading(column_indices[i], text=columns[i])
    table.pack(fill="both")
    return table

if __name__ == "__main__":
    main()