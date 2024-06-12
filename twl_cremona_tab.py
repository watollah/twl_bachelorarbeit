import tkinter as tk
from tkinter import ttk

from twl_app import TwlApp
from twl_cremona_model_diagram import CremonaModelDiagram
from twl_cremona_diagram import CremonaDiagram
from twl_cremona_control_panel import ControlPanel


class CremonaTab(ttk.Frame):

    def __init__(self, notebook: ttk.Notebook) -> None:
        ttk.Frame.__init__(self, notebook)

        vertical_panes = ttk.Panedwindow(self, orient=tk.VERTICAL)
        vertical_panes.pack(fill=tk.BOTH, expand=True)
        horizontal_panes = ttk.Panedwindow(vertical_panes, orient=tk.HORIZONTAL)
        vertical_panes.add(horizontal_panes, weight=8)

        model_diagram_frame = ttk.Frame(horizontal_panes)
        model_diagram_frame.grid_propagate(False)
        horizontal_panes.add(model_diagram_frame, weight = 1)
        self.model_diagram = self.create_model_diagram(model_diagram_frame)

        cremona_diagram_frame = ttk.Frame(horizontal_panes)
        cremona_diagram_frame.pack_propagate(False)
        horizontal_panes.add(cremona_diagram_frame, weight = 1)
        self.cremona_diagram = self.create_cremona_diagram(cremona_diagram_frame)

        control_panel_frame = ttk.Frame(vertical_panes)
        vertical_panes.add(control_panel_frame, weight=1)
        self.control_panel = self.create_control_panel(control_panel_frame)

    def create_model_diagram(self, frame: ttk.Frame) -> tk.Canvas:
        model_diagram = CremonaModelDiagram(frame)
        TwlApp.update_manager().result_widgets.append(model_diagram)

        title_label = ttk.Label(frame, text="Model", font=("Helvetica", 12))
        title_label.place(x=10, y=10)

        return model_diagram

    def create_cremona_diagram(self, frame: ttk.Frame) -> CremonaDiagram:
        cremona_diagram = CremonaDiagram(frame)
        cremona_diagram.pack(fill=tk.BOTH, expand=True)
        TwlApp.update_manager().result_widgets.append(cremona_diagram)

        title_label = ttk.Label(frame, text="Cremona Diagram", font=("Helvetica", 12))
        title_label.place(x=10, y=10)

        return cremona_diagram

    def create_control_panel(self, frame: ttk.Frame) -> 'ControlPanel':
        background_frame = ttk.Frame(frame, style="ControlPanel.TFrame") #todo: find a way to directly change panedwindow background color
        background_frame.pack(fill=tk.BOTH, expand=True)

        control_panel = ControlPanel(background_frame, self.cremona_diagram)
        control_panel.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        TwlApp.update_manager().result_widgets.append(control_panel)

        return control_panel

