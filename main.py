import tkinter as tk
from tkinter import ttk
import webbrowser

from twl_style import *
from twl_diagram import *
from twl_table import *
from twl_ui import *
from twl_io import *
from twl_settings import *
from twl_reaction_forces import *

class TwlTool(tk.Tk, TwlWidget):

    TITLE: str = "Twl Tool"

    UNIT_CONV: float = 0.025
    UNIT_SYMB: str = "m"

    def __init__(self):
        super().__init__()

        self.is_saved: tk.BooleanVar = tk.BooleanVar()
        self.is_saved.trace_add("write", lambda *ignore: self.update_window_title())
        self.is_saved.set(True)

        self.geometry("1200x800")

        init_style()

        self.update_manager = TwlUpdateManager()
        self.settings = Settings(self.update_manager)
    
        self.statical_system = StaticalSystem(self.update_manager)
        self.update_manager.widgets.append(self)
    
    
        self.create_menu_bar()

        notebook = ttk.Notebook(self)

        definition_tab = ttk.Frame(notebook)
        result_tab = ttk.Frame(notebook)
        profiles_tab = ttk.Frame(notebook)

        notebook.add(definition_tab, text="Definition")
        notebook.add(CremonaTab(notebook, self.statical_system), text="Cremona")
        notebook.add(result_tab, text="Result")
        notebook.add(profiles_tab, text="Profiles", state="disabled")

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
        paned_window.add(editor_frame, weight=2)

        diagram = TwlDiagram(editor_frame, self.statical_system, self.settings)
        diagram.pack(fill="both", expand=True)

        self.update_manager.widgets.append(diagram)
        
        #Tables
        menu_frame = ttk.Frame(paned_window)
        menu_frame.pack_propagate(False)
        paned_window.add(menu_frame, weight=1)

        nodes_entry = ToggledFrame(menu_frame, "Nodes")
        nodes_entry.pack(fill="x")
        nodes_table = TwlTable(nodes_entry.content, self.statical_system.nodes)
        nodes_table.pack(fill="both")

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

        #todo: create custom widget BorderFrame
        outer = ttk.Frame(menu_frame, style="Outer.Border.TFrame")
        outer.pack(fill="both", expand=True)
        ttk.Frame(outer, style="Inner.Border.TFrame").pack(padx=1, pady=1, fill="both", expand=True)

        self.bind("<Control-n>", lambda *ignore: clear_project(self.statical_system, self.is_saved))
        self.bind("<Control-o>", lambda *ignore: open_project(self.statical_system, self.is_saved))
        self.bind("<Control-s>", lambda *ignore: save_project(self.statical_system, self.is_saved))
        self.bind("<Control-S>", lambda *ignore: save_project_as(self.statical_system, self.is_saved))

    def update_window_title(self):
        project_name = get_project_name()
        self.title(f"{"" if self.is_saved.get() else "*"}{self.TITLE}{" - " + project_name if project_name else ""}")

    def update(self):
        if self.statical_system.is_empty():
            self.is_saved.set(True)
        else:
            self.is_saved.set(False)

    def tab_changed(self, event):
        selected_tab = event.widget.select()
        tab_index = event.widget.index(selected_tab)
        print(f"Tab changed! Selected: {tab_index}")
        if tab_index == 1:
            solver = TwlSolver(self.statical_system)
            solver.solve()

    def create_menu_bar(self):
        # Create a menu bar
        menubar = tk.Menu(self)

        # Create File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New Project", command=lambda *ignore: clear_project(self.statical_system, self.is_saved), accelerator="Ctrl+N")
        file_menu.add_separator()
        file_menu.add_command(label="Open", command=lambda *ignore: open_project(self.statical_system, self.is_saved), accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="Save", command=lambda *ignore: save_project(self.statical_system, self.is_saved), accelerator="Ctrl+S")
        file_menu.add_command(label="Save As...", command=lambda *ignore: save_project_as(self.statical_system, self.is_saved), accelerator="Ctrl+Shift+S")
        menubar.add_cascade(label="File", menu=file_menu)

        # Create Settings menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        settings_menu.add_checkbutton(label="Show Angle Guide", variable=self.settings.show_angle_guide)
        settings_menu.add_separator()
        settings_menu.add_checkbutton(label="Show Node Labels", variable=self.settings.show_node_labels)
        settings_menu.add_checkbutton(label="Show Beam Labels", variable=self.settings.show_beam_labels)
        settings_menu.add_checkbutton(label="Show Force Labels", variable=self.settings.show_force_labels)
        settings_menu.add_checkbutton(label="Show Support Labels", variable=self.settings.show_support_labels)
        settings_menu.add_separator()
        settings_menu.add_checkbutton(label="Show Grid", variable=self.settings.show_grid)
        menubar.add_cascade(label="Settings", menu=settings_menu)

        # Create Help menu and link to 
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_command(label="Help", command=lambda: webbrowser.open("https://example.com"))

        # Configure the root window to use the menu bar
        self.config(menu=menubar)

if __name__ == "__main__":
    twl_tool = TwlTool()
    twl_tool.mainloop()