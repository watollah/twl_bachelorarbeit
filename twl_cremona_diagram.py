import tkinter as tk
from tkinter import ttk
import math

from twl_app import TwlApp
from twl_style import Colors
from twl_diagram import TwlDiagram, Shape, ComponentShape
from twl_math import Point, Line, Polygon
from twl_components import Component, Node, Beam, Support, Force


class BaseLineShape(Shape):

    TAG = "baseline"
    LENGTH = 20
    SPACING = 20
    DASH = (2, 1, 1, 1)
    WIDTH = 1

    def __init__(self, pos: Point, diagram: TwlDiagram) -> None:
        super().__init__(diagram)
        line = self.get_line_coords(pos)
        tk_id = self.diagram.create_line(line.start.x, line.start.y, line.end.x, line.end.y, dash=self.DASH, tags=self.TAG)
        self.tk_shapes[tk_id] = Polygon(line.start, line.end)

    def get_line_coords(self, pos: Point) -> Line:
        return Line(Point(pos.x - self.LENGTH - self.SPACING, pos.y), Point(pos.x + self.LENGTH + self.SPACING, pos.y))


class ResultShape(ComponentShape[Force]):

    TAG: str = "result"
    WIDTH: int = 2
    SELECTED_WIDTH = 3
    ARROW_SHAPE = (12,12,4)

    SELECTED_COLOR = Colors.SELECTED
    HIGHLIGHT_COLOR = Colors.DARK_SELECTED

    def __init__(self, start: Point, end: Point, force: Force, diagram: 'CremonaDiagram') -> None:
        self.start = start
        self.end = end
        self.line_id = diagram.create_line(start.x, start.y,
                            end.x, end.y,
                            width=self.WIDTH,
                            arrow=tk.LAST, 
                            arrowshape=self.ARROW_SHAPE, 
                            tags=force.id)
        super().__init__(force, diagram)
        self.tk_shapes[self.line_id] = Polygon(self.start, self.end)

    def line_coords(self):
        return Line(self.start, self.end)

    def is_at(self, x: int, y: int) -> bool:
        return Point(x, y).distance_to_line(self.line_coords()) < self.WIDTH/2

    def default_style(self, *tags: str) -> dict[str, str]:
        return {"fill": self.COLOR, "width": str(self.WIDTH)}

    def selected_style(self, *tags: str) -> dict[str, str]:
        return {"fill": self.SELECTED_COLOR, "width": str(self.SELECTED_WIDTH)}

    def highlight(self):
        for tk_id in self.tk_shapes.keys():
            tags = self.diagram.gettags(tk_id)
            if self.LABEL_TAG in tags:
                self.diagram.itemconfig(tk_id, fill=self.HIGHLIGHT_COLOR)
            elif self.LABEL_BG_TAG not in tags:
                self.diagram.itemconfig(tk_id, fill=self.HIGHLIGHT_COLOR)

    @property
    def label_position(self) -> Point:
        return self.line_coords().midpoint()

    def label_visible(self) -> bool:
        return True

    def scale(self, factor: float):
        super().scale(factor)
        scaled_arrow = tuple(value * factor for value in self.ARROW_SHAPE)
        self.diagram.itemconfig(self.line_id, arrowshape=scaled_arrow)


class CremonaDiagram(TwlDiagram):

    START_POINT = Point(800, 50)
    SCALE = 6

    def __init__(self, master):
        super().__init__(master)
        self.support_forces: dict[Force, Support] = {}
        self.beam_forces: dict[Force, Beam] = {}
        self.forces_for_nodes: dict[Node, dict[Force, Component]] = {}
        self.steps: list[tuple[ResultShape, Component]] = []

    def create_bottom_bar(self) -> tk.Frame:
        bottom_bar = super().create_bottom_bar()
        force_spacing_check = ttk.Checkbutton(bottom_bar, takefocus=False, variable=TwlApp.settings().force_spacing, text="Force Spacing", style="Custom.TCheckbutton")
        force_spacing_check.pack(padx=self.UI_PADDING)
        return bottom_bar

    def update(self) -> None:
        self.delete("all")
        pos = self.START_POINT
        self.support_forces = {force: component for force, component in TwlApp.solver().solution.items() if isinstance(component, Support)}
        self.beam_forces = {force: component for force, component in TwlApp.solver().solution.items() if isinstance(component, Beam)}
        self.forces_for_nodes = {node: self.get_forces_for_node(node) for node in TwlApp.model().nodes}
        self.steps = []
        if TwlApp.settings().force_spacing.get():
            self.shapes.append(BaseLineShape(pos, self))
        for force in TwlApp.model().forces:
            pos = self.draw_line(pos, force, force)
        if TwlApp.settings().force_spacing.get():
            self.shapes.append(BaseLineShape(pos, self))
            pos = Point(pos.x + BaseLineShape.SPACING, pos.y)
        for force, support in self.support_forces.items():
            pos = self.draw_line(pos, force, support)
        if TwlApp.settings().force_spacing.get():
            pos = Point(pos.x - 2 * BaseLineShape.SPACING, pos.y)
        node = self.find_next_node()
        while node:
            start_angle = self.get_start_angle(self.forces_for_nodes[node])
            sorted_forces = dict(sorted(self.forces_for_nodes[node].items(), key=lambda item: (item[0].angle - start_angle) % 360))
            start_coords = self.coords(self.find_withtag(list(sorted_forces.keys())[0].id)[0])
            pos = Point(round(start_coords[2]), round(start_coords[3]))
            for force, component in sorted_forces.items():
                if type(component) == Support or type(component) == Force:
                    existing_shape = self.shape_for(force)
                    assert(isinstance(existing_shape, ResultShape))
                    self.steps.append((existing_shape, component))
                    pos = existing_shape.end
                    if TwlApp.settings().force_spacing.get():
                        pos = Point(pos.x - (pos.x - self.START_POINT.x) - BaseLineShape.SPACING, pos.y)
                else:
                    pos = self.draw_line(pos, force, component)
            self.forces_for_nodes.pop(node)
            node = self.find_next_node()
            self.update_scrollregion()

    def find_next_node(self):
        return next((node for node in self.forces_for_nodes.keys() if self.count_unknown_on_node(node) <= 2), None)

    def count_unknown_on_node(self, node) -> int:
        return sum(len(self.find_withtag(force.id)) == 0 for force in self.forces_for_nodes[node])

    def get_start_angle(self, forces: dict[Force, Component]):
        return next((force.angle for force in forces.keys() if len(self.find_withtag(force.id)) > 0 and force.strength > 0.001), 0)

    def get_forces_for_node(self, node: Node) -> dict[Force, Component]:
        forces: dict[Force, Component] = {force: force for force in node.forces}
        forces.update({force: support for force, support in self.support_forces.items() if force.node == node})
        forces.update(self.get_beam_forces_on_node(node))
        return forces

    def get_beam_forces_on_node(self, node: Node) -> dict[Force, Beam]:
        forces: dict[Force, Beam] = {}
        for beam in node.beams:
            other_node = beam.start_node if beam.start_node != node else beam.end_node
            angle = Line(Point(node.x, node.y), Point(other_node.x, other_node.y)).angle()
            strength = next((force.strength for force in TwlApp.solver().solution.keys() if force.id == beam.id))
            forces[Force.dummy(beam.id, node, angle, strength)] = beam
        return forces

    def find_start_node(self):
        return next(node for node in TwlApp.model().nodes if len(node.beams) <= 2)

    def draw_line(self, start: Point, force: Force, component: Component) -> Point:
        angle = math.radians((force.angle + 180) % 360) if type(component) == Force else math.radians(force.angle)
        end = Point(start.x + round(force.strength * math.sin(angle) * self.SCALE), start.y + (-round(force.strength * math.cos(angle) * self.SCALE)))
        shape = ResultShape(start, end, force, self)
        self.shapes.append(shape)
        self.steps.append((shape, component))
        return end