import tkinter as tk
from tkinter import ttk

from c2d_cremona_algorithm import CremonaAlgorithm
from c2d_update import Observer
from c2d_components import Component, Node, Force
from c2d_widgets import CustomMenuButton, CustomToggleButton
from c2d_cremona_model_diagram import CremonaModelDiagram
from c2d_cremona_diagram import CremonaDiagram


class ControlPanel(Observer, ttk.Frame):

    PADDING: int = 5
    SPEED_OPTIONS = {"0.5x": 2000, "1x": 1000, "2x": 500, "5x": 200}

    def __init__(self, master, model_diagram: CremonaModelDiagram, cremona_diagram: CremonaDiagram):
        super().__init__(master, style="ControlPanel.TFrame")
        self.model_diagram: CremonaModelDiagram = model_diagram
        self.cremona_diagram: CremonaDiagram = cremona_diagram

        self.steps: list[tuple[Node | None, Force, Component, bool]] = []

        self.label_text = tk.StringVar()
        self.play_state = tk.BooleanVar()
        self.selected_step = tk.IntVar()
        self.selected_speed = tk.StringVar()

        self._label = self.create_label()
        self._play_button = self.create_play_button()
        self._scale = self.create_scale()
        self._speed_selection = self.create_speed_selection()

        self.bind("<space>", lambda *ignore: self.play_state.set(not self.play_state.get()))
        self.bind("<Left>", lambda *ignore: self.selected_step.set((self.selected_step.get() - 1) % (len(self.steps) + 2)))
        self.bind("<Right>", lambda *ignore: self.selected_step.set((self.selected_step.get() + 1) % (len(self.steps) + 2)))

        focus_widgets = [self.nametowidget(self.winfo_parent()), self, self._label, self._play_button, self._scale, self._speed_selection]
        [widget.bind("<ButtonRelease-1>", lambda event: self.focus_set()) for widget in focus_widgets]

    def create_label(self):
        label_frame = ttk.Frame(self, width=400, height=30, style="ControlPanel.TFrame")
        label_frame.pack_propagate(False)
        label_frame.grid(row=0, column=1, padx=ControlPanel.PADDING, pady=ControlPanel.PADDING)
        label: ttk.Label = ttk.Label(label_frame, textvariable=self.label_text, anchor=tk.CENTER, style="ControlPanel.TLabel")
        label.pack(fill=tk.BOTH, expand=True)
        return label

    def create_play_button(self):
        play_button_frame = ttk.Frame(self, width=60, height=30)
        play_button_frame.pack_propagate(False)
        play_button_frame.grid(row=1, column=0, padx=ControlPanel.PADDING, pady=ControlPanel.PADDING)
        play_button = CustomToggleButton(play_button_frame, variable=self.play_state, text_on="\u23F8", text_off="\u23F5", command=self.run_animation, style="Play.TButton")
        play_button.pack(fill=tk.BOTH, expand=True)
        return play_button

    def create_scale(self):
        scale_frame = ttk.Frame(self, width=400, height=30, style="ControlPanel.TFrame")
        scale_frame.pack_propagate(False)
        scale_frame.grid(row=1, column=1, padx=ControlPanel.PADDING, pady=ControlPanel.PADDING)
        scale = ttk.Scale(scale_frame, from_=1, to=100, variable=self.selected_step, orient="horizontal", takefocus=False, style="TScale")
        scale.pack(fill=tk.BOTH, expand=True)
        self.selected_step.trace_add("write", lambda *ignore: self.display_step(self.selected_step.get()))
        self.selected_step.trace_add("write", lambda *ignore: self.cremona_diagram.display_step(self.selected_step.get()))
        self.selected_step.trace_add("write", lambda *ignore: self.model_diagram.display_step(self.selected_step.get()))
        self.selected_step.set(0)
        return scale

    def create_speed_selection(self):
        speed_selection_frame = ttk.Frame(self, width=60, height=30)
        speed_selection_frame.pack_propagate(False)
        speed_selection_frame.grid(row=1, column=2, padx=ControlPanel.PADDING, pady=ControlPanel.PADDING)
        speed_selection = CustomMenuButton(speed_selection_frame, self.selected_speed, list(self.SPEED_OPTIONS.keys())[1], *self.SPEED_OPTIONS.keys(), outlinewidth=1) 
        speed_selection.configure(takefocus=False)
        speed_selection.pack(fill=tk.BOTH, expand=True)
        return speed_selection

    def display_step(self, selected_step: int):
        if selected_step == 0:
            self.label_text.set("Before starting: Calculate support forces!")
        elif selected_step == len(self.cremona_diagram.steps) + 1:
            self.label_text.set("Cremona diagram complete!")
        else:
            node, force, component, sketch = self.steps[selected_step - 1]
            zero_force_hint = " \u2192 0" if not sketch and round(force.strength, 2) == 0 else ""
            self.label_text.set(f"Step {selected_step}: {"(" if sketch else ""}{f"Node {node.id}, {force.id}" if node else force.id}{")" if sketch else ""}{zero_force_hint}")

    def run_animation(self):
        if not self.play_state.get():
            return
        no_steps = len(self.steps)
        if no_steps == 0:
            return
        self.selected_step.set((self.selected_step.get() + 1) % (no_steps + 2))
        speed = self.SPEED_OPTIONS.get(self.selected_speed.get())
        assert(speed)
        self.after(speed, self.run_animation)

    def update_observer(self, component_id: str = "", attribute_id: str = ""):
        self.steps = CremonaAlgorithm.get_steps()
        self._scale.config(from_=0, to=len(self.steps) + 1)
        self.selected_step.set(len(self.steps) + 1)