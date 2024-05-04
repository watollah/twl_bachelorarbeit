import tkinter as tk

from twl_toggled_frame import *
from twl_diagram import *
from twl_table import *

def main():
    root = tk.Tk()
    root.title("TWL Tool")

    paned_window = tk.PanedWindow(root, orient=tk.HORIZONTAL, sashwidth=3, sashrelief=tk.RAISED)
    paned_window.pack(fill=tk.BOTH, expand=True)

    statical_system = StaticalSystem()

    editor_frame = tk.Frame(root)
    paned_window.add(editor_frame, minsize=300)
    paned_window.paneconfigure(editor_frame, minsize=300)

    diagram = TwlDiagram(editor_frame, statical_system)
    diagram.pack(fill="both", expand=True)

    statical_system.widgets.append(diagram)

    menu_frame = ttk.Frame(root, relief="groove", borderwidth=1)
    paned_window.add(menu_frame, minsize=300, width=300)

    beams_entry = ToggledFrame(menu_frame, "Beams")
    beams_entry.pack(fill="x")
    add_table(beams_entry.content, statical_system.beams)
    
    supports_entry = ToggledFrame(menu_frame, "Supports")
    supports_entry.pack(fill="x")
    add_table(supports_entry.content, statical_system.supports)

    forces_entry = ToggledFrame(menu_frame, "Forces")
    forces_entry.pack(fill="x")
    add_table(forces_entry.content, statical_system.forces)

    paned_window.pack(fill=tk.BOTH, expand=True)
    root.mainloop()

def add_table(menu_frame: ttk.Frame, component_list: ComponentList) -> TwlTable:
    table = TwlTable(menu_frame, component_list)
    component_list.statical_system.widgets.append(table)
    columns: tuple = component_list.component_class.attribute_names
    column_indices: tuple = tuple(f"#{i}" for i in range(1, len(columns) + 1))
    table.configure(columns=column_indices)
    table.heading("#0", text="Id")
    for i in range(0, len(columns)): table.heading(column_indices[i], text=columns[i])
    table.pack(fill="both", expand=True)
    return table

if __name__ == "__main__":
    main()