import tkinter as tk
from tkinter import ttk

from twl_components import *
from twl_widgets import *

class CremonaTab(ttk.Frame):

    def __init__(self, notebook: ttk.Notebook, statical_system: StaticalSystem) -> None:
        ttk.Frame.__init__(self, notebook)
        self.statical_system = statical_system

        vertical_panes = ttk.Panedwindow(self, orient=tk.VERTICAL)
        vertical_panes.pack(fill=tk.BOTH, expand=True)

        horizontal_panes = ttk.Panedwindow(vertical_panes, orient=tk.HORIZONTAL)
        self.create_statical_system_diagram(horizontal_panes)
        self.create_cremona_diagram(horizontal_panes)
        vertical_panes.add(horizontal_panes, weight=8)

        self.create_control_panel(vertical_panes)

    def create_statical_system_diagram(self, master: tk.PanedWindow) -> tk.Canvas:
        frame = ttk.Frame(master)
        frame.pack_propagate(False)
        master.add(frame, weight = 1)
            
        statical_system_diagram = tk.Canvas(frame)
        statical_system_diagram.pack(fill=tk.BOTH, expand=True)
    
        title_label = ttk.Label(frame, text="Statical System", font=("Helvetica", 12))
        title_label.place(x=10, y=10)
    
        return statical_system_diagram

    def create_cremona_diagram(self, master: tk.PanedWindow) -> tk.Canvas:
        frame = ttk.Frame(master)
        frame.pack_propagate(False)
        master.add(frame, weight = 1)
    
        cremona_diagram = tk.Canvas(frame)
        cremona_diagram.pack(fill=tk.BOTH, expand=True)
    
        title_label = ttk.Label(frame, text="Cremona Plan", font=("Helvetica", 12))
        title_label.place(x=10, y=10)

        return cremona_diagram
    
    CONTROL_PANEL_PADDING: int = 5

    def create_control_panel(self, master: tk.PanedWindow):
    
        frame = ttk.Frame(master, style="ControlPanel.TFrame")
        master.add(frame, weight=1)

        inner_frame = ttk.Frame(frame, style="ControlPanel.TFrame")
        inner_frame.pack(fill=tk.BOTH, expand=True)

        control_panel = ttk.Frame(inner_frame, style="ControlPanel.TFrame")
        control_panel.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    
        label_frame = ttk.Frame(control_panel, width=400, height=30, style="ControlPanel.TFrame")
        label_frame.pack_propagate(False)
        label_frame.grid(row=0, column=1, padx=CremonaTab.CONTROL_PANEL_PADDING, pady=CremonaTab.CONTROL_PANEL_PADDING)
        label: ttk.Label = ttk.Label(label_frame, anchor=tk.CENTER, style="ControlPanel.TLabel")
        label.pack(fill=tk.BOTH, expand=True)

        def run_animation():
            if not play_button.state.get():
                return
            scale_value.set((scale_value.get() + 1) % 101)
            speed = speed_options.get(selected_speed.get())
            assert(speed)
            self.after(speed, run_animation)

        play_button_frame = ttk.Frame(control_panel, width=60, height=30)
        play_button_frame.pack_propagate(False)
        play_button_frame.grid(row=1, column=0, padx=CremonaTab.CONTROL_PANEL_PADDING, pady=CremonaTab.CONTROL_PANEL_PADDING)
        play_button = CustomToggleButton(play_button_frame, text_on="\u23F8", text_off="\u23F5", command=run_animation)
        play_button.pack(fill=tk.BOTH, expand=True)

        slider_frame = ttk.Frame(control_panel, width=400, height=30, style="ControlPanel.TFrame")
        slider_frame.pack_propagate(False)
        slider_frame.grid(row=1, column=1, padx=CremonaTab.CONTROL_PANEL_PADDING, pady=CremonaTab.CONTROL_PANEL_PADDING)
        scale_value: tk.IntVar = tk.IntVar()
        scale_value.trace_add("write", lambda var, index, mode: label.config(text=f"Step {scale_value.get()}: Node X, Beam X"))
        scale = ttk.Scale(slider_frame, from_=1, to=100, variable=scale_value, orient="horizontal", takefocus=False, style="TScale")
        scale.pack(fill=tk.BOTH, expand=True)
        scale_value.set(1)

        speed_selection_frame = ttk.Frame(control_panel, width=60, height=30)
        speed_selection_frame.pack_propagate(False)
        speed_selection_frame.grid(row=1, column=2, padx=CremonaTab.CONTROL_PANEL_PADDING, pady=CremonaTab.CONTROL_PANEL_PADDING)
        speed_options = {"0.5x": 2000, "1x": 1000, "2x": 500, "5x": 200}
        selected_speed = tk.StringVar(self)
        speed_menu = CustomMenuButton(speed_selection_frame, selected_speed, list(speed_options.keys())[1], *speed_options.keys(), outlinewidth=1) 
        speed_menu.configure(takefocus=False)
        speed_menu.pack(fill=tk.BOTH, expand=True)