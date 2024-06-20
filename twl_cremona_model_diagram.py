import tkinter as tk

from twl_app import TwlApp
from twl_style import Colors
from twl_math import Point, Line, Polygon
from twl_diagram import ComponentShape
from twl_components import Component, Node, Beam, Support, Force
from twl_cremona_algorithm import CremonaAlgorithm
from twl_model_diagram import ModelDiagram, NodeShape, BeamShape, SupportShape, ForceShape


class BeamForceShape(ComponentShape[Beam]):

    TAG: str = "beam_force"

    END_OFFSET = -40
    WIDTH = 1
    D_ARROW = (12,1,10)
    Z_ARROW = (12,12,10)

    def __init__(self, beam: Beam, force: Force, diagram: 'CremonaModelDiagram') -> None:
        super().__init__(beam, diagram)
        self.force = force
        line = self.line_coords()
        self.line_id = diagram.create_line(line.start.x, line.start.y,
                            line.end.x, line.end.y,
                            width=self.WIDTH,
                            arrow=tk.BOTH, 
                            arrowshape=self.Z_ARROW if force.strength < 0 else self.D_ARROW, 
                            tags=[*self.TAGS, str(beam.id)])
        self.tk_shapes[self.line_id] = Polygon(line.start, line.end)

    def line_coords(self):
        line = Line(Point(self.component.start_node.x, self.component.start_node.y), 
                    Point(self.component.end_node.x, self.component.end_node.y))
        line.resize(self.END_OFFSET)
        return line

    def scale(self, factor: float):
        super().scale(factor)
        arrow = self.Z_ARROW if self.force.strength < 0 else self.D_ARROW
        scaled_arrow = tuple(value * factor for value in arrow)
        self.diagram.itemconfig(self.line_id, arrowshape=scaled_arrow)


class CremonaModelDiagram(ModelDiagram):

    def __init__(self, master):
        super().__init__(master)
        self.steps: list[tuple[Node | None, Force, Component, bool]] = []

    def update(self) -> None:
        super().update()
        self.steps = CremonaAlgorithm.get_steps()

        support_forces = {force: component for force, component in TwlApp.solver().solution.items() if isinstance(component, Support)}
        for force, support in support_forces.items():
            shape = ForceShape(force, self)
            self.shapes.append(shape)
            self.offset_support_force(shape, support)

        beam_forces = {force: component for force, component in TwlApp.solver().solution.items() if isinstance(component, Beam)}
        for force, beam in beam_forces.items():
            if not round(force.strength, 2) == 0:
                self.shapes.append(BeamForceShape(beam, force, self))
        self.tag_lower(BeamForceShape.TAG)
        self.refresh()

    def offset_support_force(self, shape: ForceShape, support: Support):
        force = shape.component
        if support.angle - 50 <= force.angle <= support.angle + 50:
            p1 = shape.arrow_coords().start
            line = Line(Point(force.node.x, force.node.y), Point(p1.x, p1.y))
            line.resize(SupportShape.HEIGHT)
            p2 = line.end
            shape.move(p2.x - p1.x, p2.y - p1.y)

    def display_step(self, selected_step: int):
        self.step_visibility(selected_step)
        self.step_highlighting(selected_step)

    def step_visibility(self, selected_step: int):
        [shape.set_visible(False) for shape in self.shapes if isinstance(shape, BeamForceShape)]
        if selected_step <= len(self.steps):
            for i in range(1, selected_step + 1):
                shapes = [shape for shape in self.shapes_of_type_for(BeamForceShape, self.steps[i - 1][2]) if not self.steps[i - 1][3]]
                [shape.set_visible(True) for shape in shapes]
        if selected_step == len(self.steps) + 1:
            [shape.set_visible(True) for shape in self.shapes if isinstance(shape, BeamForceShape)]

    def step_highlighting(self, selected_step: int):
        for shape in self.get_component_shapes():
            self.highlight(shape, Colors.BLACK, Colors.WHITE)
        if 0 < selected_step < len(self.steps) + 1:
            node, force, component, sketch = self.steps[selected_step - 1]
            if node:
                self.highlight(self.shapes_for(node)[0], Colors.DARK_SELECTED, Colors.SELECTED)
                for shape in self.shapes_for_node(force.node):
                    self.highlight(shape, Colors.SELECTED, Colors.WHITE)
            for shape in self.shapes_for(component):
                self.highlight(shape, Colors.DARK_SELECTED, Colors.SELECTED)

    def shapes_for_node(self, node: Node)-> list[ComponentShape]:
        return [shape for step in self.steps if step[0] == node for shape in self.shapes_for(step[2])]

    def highlight(self, shape: ComponentShape, color: str, bg_color: str):
        for tk_id in shape.tk_shapes.keys():
            tags = self.gettags(tk_id)
            if shape.LABEL_TAG in tags:
                self.itemconfig(tk_id, fill=color)
            elif shape.LABEL_BG_TAG not in tags:
                if any(tag in tags for tag in (NodeShape.TAG, SupportShape.TAG)) and not SupportShape.LINE_TAG in tags:
                    self.itemconfig(tk_id, outline=color, fill=bg_color)
                else:
                    self.itemconfig(tk_id, fill=color)