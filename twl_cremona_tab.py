import tkinter as tk
from tkinter import ttk

from twl_app import *
from twl_style import *
from twl_cremona_diagram import *
from twl_components import *
from twl_widgets import *

class CremonaTab(ttk.Frame):

    def __init__(self, notebook: ttk.Notebook) -> None:
        ttk.Frame.__init__(self, notebook)

        vertical_panes = ttk.Panedwindow(self, orient=tk.VERTICAL)
        vertical_panes.pack(fill=tk.BOTH, expand=True)
        horizontal_panes = ttk.Panedwindow(vertical_panes, orient=tk.HORIZONTAL)
        vertical_panes.add(horizontal_panes, weight=8)

        self.model_diagram = self.create_model_diagram(horizontal_panes)
        self.cremona_diagram = self.create_cremona_diagram(horizontal_panes)
        self.control_panel = self.create_control_panel(vertical_panes)

    def create_model_diagram(self, master: tk.PanedWindow) -> tk.Canvas:
        frame = ttk.Frame(master)
        frame.pack_propagate(False)
        master.add(frame, weight = 1)

        model_diagram = tk.Canvas(frame)
        model_diagram.pack(fill=tk.BOTH, expand=True)

        title_label = ttk.Label(frame, text="Model", font=("Helvetica", 12))
        title_label.place(x=10, y=10)

        return model_diagram

    def create_cremona_diagram(self, master: tk.PanedWindow) -> CremonaDiagram:
        frame = ttk.Frame(master)
        frame.pack_propagate(False)
        master.add(frame, weight = 1)
    
        cremona_diagram = CremonaDiagram(frame)
        cremona_diagram.pack(fill=tk.BOTH, expand=True)
        TwlApp.update_manager().result_widgets.append(cremona_diagram)
    
        title_label = ttk.Label(frame, text="Cremona Plan", font=("Helvetica", 12))
        title_label.place(x=10, y=10)

        return cremona_diagram

    def create_control_panel(self, master: tk.PanedWindow) -> 'ControlPanel':
        frame = ttk.Frame(master, style="ControlPanel.TFrame")
        master.add(frame, weight=1)

        inner_frame = ttk.Frame(frame, style="ControlPanel.TFrame")
        inner_frame.pack(fill=tk.BOTH, expand=True)

        control_panel = ControlPanel(inner_frame, self.cremona_diagram)
        control_panel.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        TwlApp.update_manager().result_widgets.append(control_panel)

        return control_panel


class ControlPanel(ttk.Frame, TwlWidget):

    PADDING: int = 5
    SPEED_OPTIONS = {"0.5x": 2000, "1x": 1000, "2x": 500, "5x": 200}

    def __init__(self, master, cremona_diagram: CremonaDiagram):
        super().__init__(master, style="ControlPanel.TFrame")
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
        play_button = CustomToggleButton(play_button_frame, variable=self.play_state, text_on="\u23F8", text_off="\u23F5", command=self.run_animation)
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
        visible = []
        for i in range(len(steps)):
            line_visibility = tk.HIDDEN
            if i <= self.selected_step.get() - 1:
                visible.append(steps[i][0])
            if steps[i][0] in visible:
                line_visibility = tk.NORMAL
            self.cremona_diagram.itemconfig(steps[i][0], state=line_visibility)
        if self.selected_step.get() == 0:
            self.label_text.set("")
        elif self.selected_step.get() == len(steps) + 1:
            self.label_text.set("Cremona diagram complete!")
        else:
            line, force, component = steps[self.selected_step.get() - 1]
            self.cremona_diagram.itemconfig(tk.ALL, fill=BLACK)
            for l in self.lines_for_node(force.node):
                self.cremona_diagram.itemconfig(l, fill=SELECTED) 
            self.cremona_diagram.itemconfig(line, fill=DARK_SELECTED)
            current_descr = force.id if (type(component) == Support or type(component) == Force) and visible.count(line) == 1 else f"Node {force.node.id}, {force.id}"
            self.label_text.set(f"Step {self.selected_step.get()}: {current_descr}")

    def lines_for_node(self, node: Node) -> List[int]:
        return [line for line, force, component in self.cremona_diagram.steps if force.node == node]

    def run_animation(self):
        if not self.play_state.get():
            return
        steps = len(self.cremona_diagram.steps)
        if steps == 0:
            return
        self.selected_step.set((self.selected_step.get() + 1) % steps)
        speed = self.SPEED_OPTIONS.get(self.selected_speed.get())
        assert(speed)
        self.after(speed, self.run_animation)

    def update(self) -> None:
        steps = len(self.cremona_diagram.steps) + 1
        self._scale.config(from_=0, to=steps)
        self.selected_step.set(steps)