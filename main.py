import tkinter as tk
from tkinter import ttk
import webbrowser

from twl_app import *
from twl_style import *
from twl_diagram import *
from twl_table import *
from twl_definition_tab import *
from twl_cremona_tab import *
from twl_io import *
from twl_settings import *
from twl_solver import *

class TwlTool(tk.Tk, TwlWidget):

    TITLE: str = "Twl Tool"

    def __init__(self):
        super().__init__()

        self.is_saved: tk.BooleanVar = tk.BooleanVar()
        self.is_saved.trace_add("write", lambda *ignore: self.update_window_title())
        self.is_saved.set(True)

        self.geometry("1200x800")
        init_style()    
        TwlApp.update_manager().design_widgets.append(self)
        menubar = self.create_menu_bar()
        self.config(menu=menubar)

        notebook = ttk.Notebook(self)
        notebook.add(DefinitionTab(notebook), text="Definition")
        notebook.add(CremonaTab(notebook), text="Cremona")
        notebook.add(ttk.Frame(notebook), text="Result")
        notebook.add(ttk.Frame(notebook), text="Profiles", state="disabled")
        notebook.pack(fill=tk.BOTH, expand=True)
        notebook.bind("<<NotebookTabChanged>>", self.tab_changed)

        self.bind("<Control-n>", lambda *ignore: clear_project(self.is_saved))
        self.bind("<Control-o>", lambda *ignore: open_project(self.is_saved))
        self.bind("<Control-s>", lambda *ignore: save_project(self.is_saved))
        self.bind("<Control-S>", lambda *ignore: save_project_as(self.is_saved))

    def update_window_title(self):
        project_name = get_project_name()
        self.title(f"{"" if self.is_saved.get() else "*"}{self.TITLE}{" - " + project_name if project_name else ""}")

    def update(self):
        if TwlApp.model().is_empty():
            self.is_saved.set(True)
        else:
            self.is_saved.set(False)

    def tab_changed(self, event):
        selected_tab = event.widget.select()
        tab_index = event.widget.index(selected_tab)
        print(f"Tab changed! Selected: {tab_index}")
        if tab_index == 1 or tab_index == 2:
            TwlApp.solver().solve()
            TwlApp.update_manager().update_results()

    def create_menu_bar(self):
        menubar = tk.Menu(self)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New Project", command=lambda *ignore: clear_project(self.is_saved), accelerator="Ctrl+N")
        file_menu.add_separator()
        file_menu.add_command(label="Open", command=lambda *ignore: open_project(self.is_saved), accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="Save", command=lambda *ignore: save_project(self.is_saved), accelerator="Ctrl+S")
        file_menu.add_command(label="Save As...", command=lambda *ignore: save_project_as(self.is_saved), accelerator="Ctrl+Shift+S")
        menubar.add_cascade(label="File", menu=file_menu)

        settings_menu = tk.Menu(menubar, tearoff=0)
        settings_menu.add_checkbutton(label="Show Angle Guide", variable=TwlApp.settings().show_angle_guide)
        settings_menu.add_separator()
        settings_menu.add_checkbutton(label="Show Node Labels", variable=TwlApp.settings().show_node_labels)
        settings_menu.add_checkbutton(label="Show Beam Labels", variable=TwlApp.settings().show_beam_labels)
        settings_menu.add_checkbutton(label="Show Force Labels", variable=TwlApp.settings().show_force_labels)
        settings_menu.add_checkbutton(label="Show Support Labels", variable=TwlApp.settings().show_support_labels)
        settings_menu.add_separator()
        settings_menu.add_checkbutton(label="Show Grid", variable=TwlApp.settings().show_grid)
        menubar.add_cascade(label="Settings", menu=settings_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_command(label="Help", command=lambda: webbrowser.open("https://example.com"))

        return menubar

if __name__ == "__main__":
    twl_tool = TwlTool()
    twl_tool.mainloop()