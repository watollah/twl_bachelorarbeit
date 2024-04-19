import tkinter as tk
from twl_ui import *
from toggled_frame import ToggledFrame

def main():
    root = tk.Tk()
    root.title("TWL Tool")

    statical_system = StaticalSystem()

    editor_frame = tk.Frame(root)
    editor_frame.grid(row=0, column=0, sticky="nsew")

    editor = TwlDiagram(editor_frame, statical_system)
    editor.pack(fill="both", expand=True)
    
    menu_frame = ttk.Frame(root, relief="groove", borderwidth=1)
    menu_frame.grid(row=0, column=1, sticky="nsew")

    beams_entry = ToggledFrame(menu_frame, "Beams")
    beams_entry.pack(fill="x")

    beams_table = TwlTable(beams_entry.content, statical_system.beams)
    statical_system.beams.widgets.append(beams_table)
    
    beams_table.configure(columns=("#1, #2"))
    beams_table.heading("#0", text="Id")
    beams_table.heading("#1", text="Angle")
    beams_table.heading("#2", text="Length")
    
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=0)

    beams_table.pack(fill="both", expand=True)

    root.mainloop()

if __name__ == "__main__":
    main()