import tkinter as tk
from tkinter import ttk

from c2d_app import TwlApp
from c2d_update import UpdateManager
from c2d_widgets import ToggledFrame, BorderFrame, TwlTab
from c2d_components import AngleAttribute, ForceTypeAttribute, Model, Beam, NodeAttribute, Support, Force, Result
from c2d_result_diagram import ResultDiagram
from c2d_table import TwlTable


class ResultTab(TwlTab):

    ID: str = "result_tab"

    def __init__(self, notebook: ttk.Notebook) -> None:
        super().__init__(notebook)

        horizontal_panes = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        horizontal_panes.pack(fill=tk.BOTH, expand=True)

        result_diagram_frame = ttk.Frame(horizontal_panes)
        horizontal_panes.add(result_diagram_frame, weight=2)
        self.result_diagram = self.create_diagram(result_diagram_frame)

        tables_frame = ttk.Frame(horizontal_panes)
        tables_frame.pack_propagate(False)
        horizontal_panes.add(tables_frame, weight=1)
        self.tables = self.create_tables(tables_frame)

    def update_observer(self) -> None:
        self.beams_table.component_list = self.get_result_forces(Beam)
        self.supports_table.component_list = self.get_result_forces(Support)
        [table.update_observer() for table in self.tables]
        self.result_diagram.update_observer()

    def create_diagram(self, frame: ttk.Frame):
        result_diagram = ResultDiagram(frame)
        return result_diagram

    def create_tables(self, frame: ttk.Frame):
        beams_entry = ToggledFrame(frame, "Beams")
        beams_entry.pack(fill="x")
        self.beams_table = TwlTable(beams_entry.content, self.get_result_forces(Beam), Result)
        self.beams_table.pack(fill="both")

        supports_entry = ToggledFrame(frame, "Supports")
        supports_entry.pack(fill="x")
        self.supports_table = TwlTable(supports_entry.content, self.get_result_forces(Support), Result)
        self.supports_table.pack(fill="both")
        self.supports_table.hide_columns(ForceTypeAttribute.ID)

        force_entry = ToggledFrame(frame, "Forces")
        force_entry.pack(fill="x")
        self.force_table = TwlTable(force_entry.content, TwlApp.model().forces, Force)
        self.force_table.pack(fill="both")
        self.force_table.hide_columns(NodeAttribute.ID, AngleAttribute.ID)

        BorderFrame(frame).pack(fill="both", expand=True)
        return self.beams_table, self.supports_table, self.force_table

    def get_result_forces(self, component_type: type[Beam] | type[Support]):
        model = Model(UpdateManager())
        return [Result(model, force) for force, component in TwlApp.solver().solution.items() if isinstance(component, component_type)]