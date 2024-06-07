import tkinter as tk
from tkinter import ttk

from twl_app import *
from twl_style import *
from twl_cremona_diagram import *
from twl_components import *
from twl_widgets import *
from twl_diagram import *
from twl_table import *

class DefinitionTab(ttk.Frame):

    def __init__(self, notebook: ttk.Notebook) -> None:
        ttk.Frame.__init__(self, notebook)

        paned_window = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True)

        definition_diagram_frame = ttk.Frame(paned_window)
        paned_window.add(definition_diagram_frame, weight=2)
        self.toolbar = self.create_toolbar(definition_diagram_frame)
        self.definition_diagram = self.create_diagram(definition_diagram_frame)
        self.tables = self.create_tables(paned_window)

    def create_toolbar(self, master: ttk.Frame):
        toolbar: ttk.Frame = ttk.Frame(master, style="Diagram.TFrame")
        toolbar.pack(side=tk.LEFT, fill=tk.Y)
        return toolbar

    def create_diagram(self, master: ttk.Frame):
        editor_frame = ttk.Frame(master)
        editor_frame.pack(fill="both", expand=True)
        diagram = TwlDiagram(editor_frame, self.toolbar)
        TwlApp.update_manager().design_widgets.append(diagram)

    def create_tables(self, master: tk.PanedWindow):
        menu_frame = ttk.Frame(master)
        menu_frame.pack_propagate(False)
        master.add(menu_frame, weight=1)

        nodes_entry = ToggledFrame(menu_frame, "Nodes")
        nodes_entry.pack(fill="x")
        nodes_table = TwlTable(nodes_entry.content, TwlApp.model().nodes)
        nodes_table.pack(fill="both")

        beams_entry = ToggledFrame(menu_frame, "Beams")
        beams_entry.pack(fill="x")
        beams_table = TwlTable(beams_entry.content, TwlApp.model().beams)
        beams_table.pack(fill="both")
        
        supports_entry = ToggledFrame(menu_frame, "Supports")
        supports_entry.pack(fill="x")
        supports_table = TwlTable(supports_entry.content, TwlApp.model().supports)
        supports_table.pack(fill="both")

        forces_entry = ToggledFrame(menu_frame, "Forces")
        forces_entry.pack(fill="x")
        forces_table = TwlTable(forces_entry.content, TwlApp.model().forces)
        forces_table.pack(fill="both")

        #todo: create custom widget BorderFrame
        outer = ttk.Frame(menu_frame, style="Outer.Border.TFrame")
        outer.pack(fill="both", expand=True)
        ttk.Frame(outer, style="Inner.Border.TFrame").pack(padx=1, pady=1, fill="both", expand=True)

