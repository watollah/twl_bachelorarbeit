"""C2D - The digital Cremona Diagram"""
__author__ = "Hannes Watolla"
__version__ = "1.0.0"

import sys
import tkinter as tk
from tkinter import ttk
import webbrowser

import c2d_io as io
from c2d_app import TwlApp
from c2d_update import Observer
from c2d_style import init_style
from c2d_images import get_image_path
from c2d_definition_tab import DefinitionTab
from c2d_cremona_tab import CremonaTab
from c2d_result_tab import ResultTab


class C2D(Observer, tk.Tk):
    """Class that represents the root widget (the window) of the application."""

    TITLE: str = "C2D"
    ICON: str = "c2d_icon"

    def __init__(self):
        """Create an instance of TwlTool."""
        super().__init__()

        TwlApp.saved_state().trace_add("write", lambda *ignore: self.update_window_title())
        TwlApp.saved_state().set(True)

        self.geometry("1200x800")
        self.iconbitmap(get_image_path(self.ICON, "ico"))
        init_style()
        menubar = self.create_menu_bar()
        self.config(menu=menubar)

        self.notebook = ttk.Notebook(self)
        self.definition_tab = DefinitionTab(self.notebook)
        self.notebook.add(self.definition_tab, text="Definition")
        self.cremona_tab = CremonaTab(self.notebook)
        self.notebook.add(self.cremona_tab, text="Cremona", state=tk.DISABLED)
        self.result_tab = ResultTab(self.notebook)
        self.notebook.add(self.result_tab, text="Result", state=tk.DISABLED)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        self.notebook.bind("<<NotebookTabChanged>>", self.tab_changed)

        self.bind("<Control-n>", lambda *ignore: io.new_project())
        self.bind("<Control-o>", lambda *ignore: self.open_project())
        self.bind("<Control-s>", lambda *ignore: io.save_project())
        self.bind("<Control-S>", lambda *ignore: io.save_project_as())

        TwlApp.update_manager().register_observer(self)

    def open_project(self):
        """Open a project from the file system. If opening is successful switch to the definition tab.
        This is done in case the opened Model is invalid and cremona and result tab have to be disabled."""
        if io.open_project():
            self.notebook.select(0)

    def update_window_title(self):
        """Update the window title with the current projects file name. Also adds an asterix if there are unsaved changes."""
        project_name = io.get_project_name()
        self.title(f"{"" if TwlApp.saved_state().get() else "*"}{self.TITLE}{" - " + project_name if project_name else ""}")

    def update_observer(self, component_id: str = "", attribute_id: str = ""):
        """Update the state of cremona and result tab depending on the Model being valid."""
        model = TwlApp.model()
        tab_state = tk.NORMAL if model.is_valid() else tk.DISABLED
        self.notebook.tab(self.cremona_tab, state=tab_state)
        self.notebook.tab(self.result_tab, state=tab_state)
        TwlApp.saved_state().set(model.is_empty())
        TwlApp.changed_state().set(not model.is_empty())

    def tab_changed(self, event):
        """Executed when the tab of the application is changed. 
        If there are changes to the Model run the solver and update the cremona and result tab."""
        selected_tab = event.widget.nametowidget(event.widget.select())
        if isinstance(selected_tab, CremonaTab) or isinstance(selected_tab, ResultTab):
            if TwlApp.changed_state().get():
                TwlApp.solver().solve()
                self.cremona_tab.update_observer()
                self.result_tab.update_observer()
                TwlApp.changed_state().set(False)
        if isinstance(selected_tab, CremonaTab):
            selected_tab.control_panel.focus_set()

    def create_menu_bar(self):
        """Create the menu bar at the top of the application."""
        menubar = tk.Menu(self)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New Project", command=lambda *ignore: io.new_project(), accelerator="Ctrl+N")
        file_menu.add_separator()
        file_menu.add_command(label="Open", command=lambda *ignore: self.open_project(), accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="Save", command=lambda *ignore: io.save_project(), accelerator="Ctrl+S")
        file_menu.add_command(label="Save As...", command=lambda *ignore: io.save_project_as(), accelerator="Ctrl+Shift+S")
        menubar.add_cascade(label="File", menu=file_menu)

        settings_menu = tk.Menu(menubar, tearoff=0)
        model_diagrams_menu = tk.Menu(settings_menu, tearoff=0)
        model_diagrams_menu.add_checkbutton(label="Show Angle Guide", variable=TwlApp.settings().show_angle_guide)
        model_diagrams_menu.add_checkbutton(label="Show Grid", variable=TwlApp.settings().show_grid)
        model_diagrams_menu.add_separator()
        model_diagrams_menu.add_checkbutton(label="Show Node Labels", variable=TwlApp.settings().show_node_labels)
        model_diagrams_menu.add_checkbutton(label="Show Beam Labels", variable=TwlApp.settings().show_beam_labels)
        model_diagrams_menu.add_checkbutton(label="Show Force Labels", variable=TwlApp.settings().show_force_labels)
        model_diagrams_menu.add_checkbutton(label="Show Support Labels", variable=TwlApp.settings().show_support_labels)
        settings_menu.add_cascade(label="Model Diagrams", menu=model_diagrams_menu)
        cremona_diagram_menu = tk.Menu(settings_menu, tearoff=0)
        cremona_diagram_menu.add_checkbutton(label="Force Spacing", variable=TwlApp.settings().force_spacing)
        cremona_diagram_menu.add_separator()
        cremona_diagram_menu.add_checkbutton(label="Show Labels", variable=TwlApp.settings().show_cremona_labels)
        settings_menu.add_cascade(label="Cremona Diagram", menu=cremona_diagram_menu)
        menubar.add_cascade(label="Settings", menu=settings_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_command(label="Help", command=lambda: webbrowser.open("https://github.com/watollah/twl_bachelorarbeit/releases/download/C2D/Quickstart.pdf"))

        return menubar


if __name__ == "__main__":
    """Runs the mainloop (shows the window) of the application when it is started. 
    If a file is passed in the start arguments (when a user double clicked on a .c2d file to start the application) 
    then load the Model from the file on startup."""
    c2d = C2D()
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        io.open_project(file_path)
    c2d.mainloop()