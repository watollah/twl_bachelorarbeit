import tkinter as tk
from tkinter import ttk
import webbrowser

import twl_io as io
from twl_app import TwlApp
from twl_update import Observer
from twl_style import init_style
from twl_definition_tab import DefinitionTab
from twl_cremona_tab import CremonaTab
from twl_result_tab import ResultTab


class TwlTool(Observer, tk.Tk):

    TITLE: str = "C2D"

    def __init__(self):
        super().__init__()

        TwlApp.saved_state().trace_add("write", lambda *ignore: self.update_window_title())
        TwlApp.saved_state().set(True)

        self.geometry("1200x800")
        init_style()
        TwlApp.update_manager().register_observer(self)
        menubar = self.create_menu_bar()
        self.config(menu=menubar)

        notebook = ttk.Notebook(self)
        self.definition_tab = DefinitionTab(notebook)
        notebook.add(self.definition_tab, text="Definition")
        self.cremona_tab = CremonaTab(notebook)
        notebook.add(self.cremona_tab, text="Cremona")
        self.result_tab = ResultTab(notebook)
        notebook.add(self.result_tab, text="Result")
        notebook.pack(fill=tk.BOTH, expand=True)
        notebook.bind("<<NotebookTabChanged>>", self.tab_changed)

        self.bind("<Control-n>", lambda *ignore: io.clear_project())
        self.bind("<Control-o>", lambda *ignore: io.open_project())
        self.bind("<Control-s>", lambda *ignore: io.save_project())
        self.bind("<Control-S>", lambda *ignore: io.save_project_as())

    def update_window_title(self):
        project_name = io.get_project_name()
        self.title(f"{"" if TwlApp.saved_state().get() else "*"}{self.TITLE}{" - " + project_name if project_name else ""}")

    def update_observer(self, component_id: str = "", attribute_id: str = ""):
        if TwlApp.model().is_empty():
            TwlApp.saved_state().set(True)
        else:
            TwlApp.saved_state().set(False)
            TwlApp.changed_state().set(True)

    def tab_changed(self, event):
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
        menubar = tk.Menu(self)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New Project", command=lambda *ignore: io.clear_project(), accelerator="Ctrl+N")
        file_menu.add_separator()
        file_menu.add_command(label="Open", command=lambda *ignore: io.open_project(), accelerator="Ctrl+O")
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
        menubar.add_command(label="Help", command=lambda: webbrowser.open("https://example.com"))

        return menubar


if __name__ == "__main__":
    twl_tool = TwlTool()
    twl_tool.mainloop()