import tkinter as tk
from tkinter import ttk

from twl_update import TwlWidget
from twl_style import Colors
from twl_components import Node, Support, Force
from twl_widgets import CustomMenuButton, CustomToggleButton
from twl_cremona_model_diagram import CremonaModelDiagram
from twl_cremona_diagram import CremonaDiagram, ResultShape, BaseLineShape


class ControlPanel(ttk.Frame, TwlWidget):

    PADDING: int = 5
    SPEED_OPTIONS = {"0.5x": 2000, "1x": 1000, "2x": 500, "5x": 200}

    def __init__(self, master, model_diagram: CremonaModelDiagram, cremona_diagram: CremonaDiagram):
        super().__init__(master, style="ControlPanel.TFrame")
        self.model_diagram: CremonaModelDiagram = model_diagram
        self.cremona_diagram: CremonaDiagram = cremona_diagram

        self.label_text = tk.StringVar()
        self.play_state = tk.BooleanVar()
        self.selected_step = tk.IntVar()
        self.selected_speed = tk.StringVar()

        self._label = self.create_label()
        self._play_button = self.create_play_button()
        self._scale = self.create_scale()
        self._speed_selection = self.create_speed_selection()

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
        self.selected_step.trace_add("write", lambda *ignore: self.display_selected_step())
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

    def display_selected_step(self):
        steps = self.cremona_diagram.steps
        visible: list[ResultShape] = []
        for i in range(len(steps)):
            line_visibility = tk.HIDDEN
            if i <= self.selected_step.get() - 1:
                visible.append(steps[i][0])
            if steps[i][0] in visible:
                line_visibility = tk.NORMAL
            if round(steps[i][0].component.strength, 2) == 0:
                line_visibility = tk.HIDDEN
            for tk_id in steps[i][0].tk_shapes.keys():
                self.cremona_diagram.itemconfig(tk_id, state=line_visibility)

        if self.selected_step.get() == 0:
            self.label_text.set("")
        elif self.selected_step.get() == len(steps) + 1:
            for shape in self.cremona_diagram.selection:
                shape.deselect()
            self.label_text.set("Cremona diagram complete!")
        else:
            current_shape, component = steps[self.selected_step.get() - 1]
            for shape in self.cremona_diagram.selection:
                shape.deselect()
            for shape in self.shapes_for_node(current_shape.component.node):
                shape.select()
            current_shape.highlight()
            #self.cremona_diagram.itemconfig(line, fill=Colors.DARK_SELECTED)
            current_descr = current_shape.component.id if (type(component) == Support or type(component) == Force) and visible.count(current_shape) == 1 else f"Node {current_shape.component.node.id}, {current_shape.component.id}"
            self.label_text.set(f"Step {self.selected_step.get()}: {current_descr}")

    def shapes_for_node(self, node: Node) -> list[ResultShape]:
        return [shape for shape, component in self.cremona_diagram.steps if shape.component.node == node]

    def run_animation(self):
        if not self.play_state.get():
            return
        steps = len(self.cremona_diagram.steps)
        if steps == 0:
            return
        self.selected_step.set((self.selected_step.get() + 1) % (steps + 2))
        speed = self.SPEED_OPTIONS.get(self.selected_speed.get())
        assert(speed)
        self.after(speed, self.run_animation)

    def update(self) -> None:
        steps = len(self.cremona_diagram.steps) + 1
        self._scale.config(from_=0, to=steps)
        self.selected_step.set(steps)