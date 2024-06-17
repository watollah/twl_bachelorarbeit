import tkinter as tk
from tkinter import ttk
import math

from twl_app import TwlApp
from twl_style import Colors
from twl_diagram import TwlDiagram, Shape, ComponentShape
from twl_math import Point, Line, Polygon
from twl_cremona_algorithm import CremonaAlgorithm
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
        self.steps = []

    def create_bottom_bar(self) -> tk.Frame:
        bottom_bar = super().create_bottom_bar()
        force_spacing_check = ttk.Checkbutton(bottom_bar, takefocus=False, variable=TwlApp.settings().force_spacing, text="Force Spacing", style="Custom.TCheckbutton")
        force_spacing_check.pack(padx=self.UI_PADDING)
        return bottom_bar

    def update(self) -> None:
        self.clear()
        self.steps = CremonaAlgorithm.get_steps()
        pos = self.START_POINT
        for node, force, component in self.steps:
            if node and self.find_withtag(force.id):
                coords = self.coords(self.find_withtag(force.id)[0])
                pos = Point(round(coords[2]), round(coords[3]))
                if isinstance(component, Support) or isinstance(component, Force):
                    continue
            pos = self.draw_force(pos, force, component)
        if self.steps and TwlApp.settings().force_spacing.get():
            self.force_spacing()
        self.update_scrollregion()

    def draw_force(self, start: Point, force: Force, component: Component) -> Point:
        angle = math.radians((force.angle + 180) % 360) if type(component) == Force else math.radians(force.angle)
        start = Point(start.x, start.y)
        end = Point(start.x + round(force.strength * math.sin(angle) * self.SCALE), start.y + (-round(force.strength * math.cos(angle) * self.SCALE)))
        self.shapes.append(ResultShape(start, end, force, self))
        return end

    def force_spacing(self):
        force_forces = [force for node, force, component in self.steps if not node and isinstance(component, Force)]
        [self.shape_for(force).move(BaseLineShape.SPACING, 0) for force in force_forces]
        support_forces = [force for node, force, component in self.steps if not node and isinstance(component, Support)]
        [self.shape_for(force).move(2 * BaseLineShape.SPACING, 0) for force in support_forces]
        self.shapes.append(BaseLineShape(Point(self.START_POINT.x + BaseLineShape.SPACING, self.START_POINT.y), self))
        coords = self.coords(self.find_withtag(force_forces[len(force_forces) - 1].id)[0])
        self.shapes.append(BaseLineShape(Point(round(coords[2]), round(coords[3])), self))

    def display_step(self, selected_step: int):
        visible: set[Shape] = set()
        for i, step in enumerate(self.steps):
            shape = self.shape_for(step[1])
            if i <= selected_step - 1 and not round(step[1].strength, 2) == 0:
                visible.add(shape)
            shape.set_visible(shape in visible)

        for shape in self.selection.copy():
            shape.deselect()
        if 0 < selected_step < len(self.steps) + 1:
            node, force, component = self.steps[selected_step - 1]
            if node:
                for shape in self.shapes_for_node(force.node):
                    shape.select()
            current_shape = self.shape_for(force)
            assert(isinstance(current_shape, ResultShape))
            current_shape.select()
            current_shape.highlight()

    def shapes_for_node(self, node: Node) -> list[ComponentShape]:
        return [self.shape_for(step[1]) for step in self.steps if step[0] == node]