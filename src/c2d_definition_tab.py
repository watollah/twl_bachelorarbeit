import tkinter as tk
from tkinter import ttk

from c2d_app import TwlApp
from c2d_widgets import ToggledFrame, BorderFrame, TwlTab
from c2d_components import Node, Beam, Support, Force
from c2d_definition_diagram import DefinitionDiagram
from c2d_table import TwlTable


class DefinitionTab(TwlTab):

    ID: str = "definition_tab"

    def __init__(self, notebook: ttk.Notebook) -> None:
        super().__init__(notebook)

        horizontal_panes = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        horizontal_panes.pack(fill=tk.BOTH, expand=True)

        definition_diagram_frame = ttk.Frame(horizontal_panes)
        horizontal_panes.add(definition_diagram_frame, weight=2)
        self.definition_diagram = self.create_diagram(definition_diagram_frame)

        tables_frame = ttk.Frame(horizontal_panes)
        tables_frame.pack_propagate(False)
        horizontal_panes.add(tables_frame, weight=1)
        self.tables = self.create_tables(tables_frame)

    def create_diagram(self, frame: ttk.Frame):
        diagram = DefinitionDiagram(frame)
        TwlApp.update_manager().register_observer(diagram)
        return diagram

    def create_tables(self, frame: ttk.Frame):
        nodes_entry = ToggledFrame(frame, "Nodes")
        nodes_entry.pack(fill="x")
        nodes_table = TwlTable(nodes_entry.content, TwlApp.model().nodes, Node)
        nodes_table.pack(fill="both")
        TwlApp.update_manager().register_observer(nodes_table)

        beams_entry = ToggledFrame(frame, "Beams")
        beams_entry.pack(fill="x")
        beams_table = TwlTable(beams_entry.content, TwlApp.model().beams, Beam)
        beams_table.pack(fill="both")
        TwlApp.update_manager().register_observer(beams_table)
        
        supports_entry = ToggledFrame(frame, "Supports")
        supports_entry.pack(fill="x")
        supports_table = TwlTable(supports_entry.content, TwlApp.model().supports, Support)
        supports_table.pack(fill="both")
        TwlApp.update_manager().register_observer(supports_table)

        forces_entry = ToggledFrame(frame, "Forces")
        forces_entry.pack(fill="x")
        forces_table = TwlTable(forces_entry.content, TwlApp.model().forces, Force)
        forces_table.pack(fill="both")
        TwlApp.update_manager().register_observer(forces_table)

        BorderFrame(frame).pack(fill="both", expand=True)
        return nodes_table, beams_table, supports_table, forces_table