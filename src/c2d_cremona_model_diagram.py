import tkinter as tk

from c2d_style import Colors
from c2d_diagram import ComponentShape
from c2d_components import Component, Node, Force
from c2d_cremona_algorithm import CremonaAlgorithm
from c2d_result_model_diagram import ResultModelDiagram, BeamForceShape
from c2d_model_diagram import NodeShape, SupportShape, ForceShape


class CremonaModelDiagram(ResultModelDiagram):

    def __init__(self, master, selected_step: tk.IntVar):
        """Create an instance of CremonaModelDiagram."""
        super().__init__(master)
        self.selected_step: tk.IntVar = selected_step
        self.selected_step.trace_add("write", lambda *ignore: self.display_step(self.selected_step.get()))
        self.steps: list[tuple[Node | None, Force, Component, bool]] = []

    def update_observer(self, component_id: str="", attribute_id: str=""):
        super().update_observer(component_id, attribute_id)
        self.steps = CremonaAlgorithm.get_steps()

    def display_step(self, selected_step: int):
        self.step_visibility(selected_step)
        self.step_highlighting(selected_step)
        self.adjust_label_positions()
        self.refresh()

    def step_visibility(self, selected_step: int):
        [shape.set_visible(False) for shape in self.shapes if isinstance(shape, BeamForceShape)]
        if selected_step <= len(self.steps):
            for i in range(1, selected_step + 1):
                shapes = [shape for shape in self.shapes_of_type_for(BeamForceShape, self.steps[i - 1][2]) if not self.steps[i - 1][3]]
                [shape.set_visible(True) for shape in shapes]
        if selected_step == len(self.steps) + 1:
            [shape.set_visible(True) for shape in self.shapes if isinstance(shape, BeamForceShape)]

    def step_highlighting(self, selected_step: int):
        for shape in self.component_shapes:
            self.highlight(shape, Colors.BLACK, Colors.WHITE)
        if 0 < selected_step < len(self.steps) + 1:
            node, force, component, sketch = self.steps[selected_step - 1]
            if node:
                self.highlight(self.shapes_for(node)[0], Colors.DARK_SELECTED, Colors.SELECTED)
                for shape in self.shapes_for_node(force.node):
                    self.highlight(shape, Colors.SELECTED, Colors.WHITE)
            current_shapes = set(self.shapes_for(component))
            current_shapes.update(self.shapes_for(force))
            for shape in current_shapes:
                self.highlight(shape, Colors.DARK_SELECTED, Colors.SELECTED)

    def highlight(self, shape: ComponentShape, color: str, bg_color: str):
        for tk_id in shape.tk_shapes.keys():
            tags = self.gettags(tk_id)
            if shape.LABEL_TAG in tags:
                self.itemconfig(tk_id, fill=color)
            elif shape.LABEL_BG_TAG not in tags:
                if any(tag in tags for tag in (NodeShape.TAG, SupportShape.TAG)) and not SupportShape.LINE_TAG in tags:
                    self.itemconfig(tk_id, outline=color, fill=bg_color)
                elif isinstance(shape, BeamForceShape) and round(shape.force.strength, 2) == 0:
                    self.itemconfig(tk_id, outline=color, fill=Colors.WHITE)
                else:
                    self.itemconfig(tk_id, fill=color)

    def shapes_for_node(self, node: Node)-> list[ComponentShape]:
        shapes: set[ComponentShape] = {shape for step in self.steps if step[0] == node for shape in self.shapes_for(step[2])}
        shapes.update({shape for shape in self.shapes if isinstance(shape, ForceShape) and shape.component.node == node})
        return list(shapes)