import tkinter as tk
from tkinter import ttk
import webbrowser

from twl_toggled_frame import *
from twl_diagram import *
from twl_table import *
from twl_ui import *
from twl_io import *

class TwlTool(tk.Tk, TwlWidget):

    TITLE: str = "Twl Tool"

    def __init__(self):
        super().__init__()

        self.is_saved: tk.BooleanVar = tk.BooleanVar()
        self.is_saved.trace_add("write", lambda *ignore: self.title(f"{"" if self.is_saved.get() else "*"}{self.TITLE}"))
        self.is_saved.set(True)

        self.geometry("1200x800")

        self.configure_styles()

        self.statical_system = StaticalSystem()
        self.statical_system.widgets.append(self)

        self.create_menu_bar()

        notebook = ttk.Notebook(self)

        definition_tab = ttk.Frame(notebook)
        result_tab = ttk.Frame(notebook)
        profiles_tab = ttk.Frame(notebook)

        notebook.add(definition_tab, text="Definition")
        notebook.add(CremonaTab(notebook, self.statical_system), text="Cremona")
        notebook.add(result_tab, text="Result")
        notebook.add(profiles_tab, text="(Profiles)")

        label3 = tk.Label(result_tab, text="Results")
        label3.pack(padx=10, pady=10)

        label4 = tk.Label(profiles_tab, text="Profiles (maybe added later)")
        label4.pack(padx=10, pady=10)

        notebook.bind("<<NotebookTabChanged>>", self.tab_changed)
        notebook.pack(fill=tk.BOTH, expand=True)

        paned_window = ttk.PanedWindow(definition_tab, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True)

        #Diagram Editor
        editor_frame = ttk.Frame(paned_window)
        editor_frame.pack_propagate(False)
        paned_window.add(editor_frame, weight=3)

        diagram = TwlDiagram(editor_frame, self.statical_system)
        diagram.pack(fill="both", expand=True)

        self.statical_system.widgets.append(diagram)
        
        #Tables
        menu_frame = ttk.Frame(paned_window)
        menu_frame.pack_propagate(False)
        paned_window.add(menu_frame, weight=1)

        beams_entry = ToggledFrame(menu_frame, "Beams")
        beams_entry.pack(fill="x")
        beams_table = TwlTable(beams_entry.content, self.statical_system.beams)
        beams_table.pack(fill="both")
        
        supports_entry = ToggledFrame(menu_frame, "Supports")
        supports_entry.pack(fill="x")
        supports_table = TwlTable(supports_entry.content, self.statical_system.supports)
        supports_table.pack(fill="both")

        forces_entry = ToggledFrame(menu_frame, "Forces")
        forces_entry.pack(fill="x")
        forces_table = TwlTable(forces_entry.content, self.statical_system.forces)
        forces_table.pack(fill="both")

        self.bind("<Control-s>", lambda *ignore: self.is_saved.set(save_project(self.statical_system)))
        self.bind("<Control-o>", lambda *ignore: open_project(self.statical_system, self.is_saved.get()))

    def update(self):
        if self.statical_system.is_empty():
            self.is_saved.set(True)
        else:
            self.is_saved.set(False)

    def tab_changed(self, event):
        print("Tab changed!")

    def configure_styles(self):
        style = ttk.Style()
        style.configure('TNotebook.Tab', padding=(20, 10), font=("Helvetica", 12))

    def create_menu_bar(self):
        # Create a menu bar
        menubar = tk.Menu(self)

        # Create File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open", command=lambda *ignore: open_project(self.statical_system, self.is_saved.get()), accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="Save", command=lambda *ignore: self.is_saved.set(save_project(self.statical_system)), accelerator="Ctrl+S")
        file_menu.add_command(label="Save As...", command=lambda *ignore: save_project(self.statical_system))
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
        self.config(menu=menubar)

if __name__ == "__main__":
    twl_tool = TwlTool()
    twl_tool.mainloop()