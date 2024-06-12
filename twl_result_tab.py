import tkinter as tk
from tkinter import ttk

from twl_app import TwlApp
from twl_widgets import ToggledFrame, BorderFrame
from twl_result_diagram import ResultDiagram
from twl_table import TwlTable


class ResultTab(ttk.Frame):

    def __init__(self, notebook: ttk.Notebook) -> None:
        ttk.Frame.__init__(self, notebook)

        horizontal_panes = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        horizontal_panes.pack(fill=tk.BOTH, expand=True)

        result_diagram_frame = ttk.Frame(horizontal_panes)
        horizontal_panes.add(result_diagram_frame, weight=2)
        self.result_diagram = self.create_diagram(result_diagram_frame)

        tables_frame = ttk.Frame(horizontal_panes)
        tables_frame.pack_propagate(False)
        horizontal_panes.add(tables_frame, weight=1)
        self.tables = self.create_tables(tables_frame)

    def create_diagram(self, frame: ttk.Frame):
        diagram = ResultDiagram(frame)
        TwlApp.update_manager().result_widgets.append(diagram)

    def create_tables(self, frame: ttk.Frame):
        nodes_entry = ToggledFrame(frame, "Support Forces")
        nodes_entry.pack(fill="x")
        nodes_table = TwlTable(nodes_entry.content, TwlApp.model().nodes)
        nodes_table.pack(fill="both")

        beams_entry = ToggledFrame(frame, "Beam Forces")
        beams_entry.pack(fill="x")
        beams_table = TwlTable(beams_entry.content, TwlApp.model().beams)
        beams_table.pack(fill="both")

        BorderFrame(frame).pack(fill="both", expand=True)