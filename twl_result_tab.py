import tkinter as tk
from tkinter import ttk

from twl_app import TwlApp
from twl_update import UpdateManager
from twl_widgets import ToggledFrame, BorderFrame, TwlTab
from twl_components import AngleAttribute, ForceTypeAttribute, Model, Beam, NodeAttribute, Support, Force, Result
from twl_result_diagram import ResultDiagram
from twl_table import TwlTable


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
        self.beams_table.component_list = self.get_beam_forces()
        self.beams_table.update_observer()
        self.supports_table.component_list = self.get_support_forces()
        self.supports_table.update_observer()
        self.force_table.update_observer()
        self.result_diagram.update_observer()

    def create_diagram(self, frame: ttk.Frame):
        result_diagram = ResultDiagram(frame)
        return result_diagram

    def create_tables(self, frame: ttk.Frame):
        beams_entry = ToggledFrame(frame, "Beams")
        beams_entry.pack(fill="x")
        self.beams_table = TwlTable(beams_entry.content, self.get_beam_forces(), Result)
        self.beams_table.pack(fill="both")

        supports_entry = ToggledFrame(frame, "Supports")
        supports_entry.pack(fill="x")
        self.supports_table = TwlTable(supports_entry.content, self.get_support_forces(), Result)
        self.supports_table.pack(fill="both")
        self.supports_table.hide_columns(ForceTypeAttribute.ID)

        force_entry = ToggledFrame(frame, "Forces")
        force_entry.pack(fill="x")
        self.force_table = TwlTable(force_entry.content, TwlApp.model().forces, Force)
        self.force_table.pack(fill="both")
        self.force_table.hide_columns(NodeAttribute.ID, AngleAttribute.ID)

        BorderFrame(frame).pack(fill="both", expand=True)

    def get_beam_forces(self):
        model = Model(UpdateManager())
        return [Result(model, force) for force, component in TwlApp.solver().solution.items() if isinstance(component, Beam)]

    def get_support_forces(self):
        model = Model(UpdateManager())
        return [Result(model, force) for force, component in TwlApp.solver().solution.items() if isinstance(component, Support)]