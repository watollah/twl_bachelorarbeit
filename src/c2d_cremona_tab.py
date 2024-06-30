import tkinter as tk
from tkinter import ttk

from c2d_cremona_model_diagram import CremonaModelDiagram
from c2d_cremona_diagram import CremonaDiagram
from c2d_cremona_control_panel import ControlPanel
from c2d_widgets import TwlTab


class CremonaTab(TwlTab):

    ID: str = "cremona_tab"

    def __init__(self, notebook: ttk.Notebook) -> None:
        """Create an instance of CremonaTab."""
        super().__init__(notebook)
        self.selected_step = tk.IntVar()

        vertical_panes = ttk.Panedwindow(self, orient=tk.VERTICAL)
        vertical_panes.pack(fill=tk.BOTH, expand=True)
        horizontal_panes = ttk.Panedwindow(vertical_panes, orient=tk.HORIZONTAL)
        vertical_panes.add(horizontal_panes, weight=8)

        model_diagram_frame = ttk.Frame(horizontal_panes)
        model_diagram_frame.grid_propagate(False)
        horizontal_panes.add(model_diagram_frame, weight = 1)
        self.model_diagram = self.create_model_diagram(model_diagram_frame)

        cremona_diagram_frame = ttk.Frame(horizontal_panes)
        cremona_diagram_frame.grid_propagate(False)
        horizontal_panes.add(cremona_diagram_frame, weight = 1)
        self.cremona_diagram = self.create_cremona_diagram(cremona_diagram_frame)

        control_panel_frame = ttk.Frame(vertical_panes)
        vertical_panes.add(control_panel_frame, weight=1)
        self.control_panel = self.create_control_panel(control_panel_frame)

    def create_model_diagram(self, frame: ttk.Frame) -> CremonaModelDiagram:
        model_diagram = CremonaModelDiagram(frame, self.selected_step)
        ttk.Label(frame, text="Model", font=("Helvetica", 12)).place(x=10, y=10)
        return model_diagram

    def create_cremona_diagram(self, frame: ttk.Frame) -> CremonaDiagram:
        cremona_diagram = CremonaDiagram(frame, self.selected_step)
        ttk.Label(frame, text="Cremona Diagram", font=("Helvetica", 12)).place(x=10, y=10)
        return cremona_diagram

    def create_control_panel(self, frame: ttk.Frame) -> 'ControlPanel':
        background_frame = ttk.Frame(frame, style="ControlPanel.TFrame")
        background_frame.pack(fill=tk.BOTH, expand=True)
        control_panel = ControlPanel(background_frame, self.selected_step)
        control_panel.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        return control_panel

    def update_observer(self, component_id: str = "", attribute_id: str = ""):
        self.model_diagram.update_observer(component_id, attribute_id)
        self.cremona_diagram.update_observer(component_id, attribute_id)
        self.control_panel.update_observer(component_id, attribute_id)