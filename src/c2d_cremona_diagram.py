import tkinter as tk
from tkinter import ttk
from typing import Any
import math

from c2d_app import TwlApp
from c2d_style import Colors
from c2d_diagram import TwlDiagram, Shape, ComponentShape
from c2d_math import Point, Line, Polygon
from c2d_cremona_algorithm import CremonaAlgorithm
from c2d_components import Component, Node, Support, Force


class BaseLineShape(Shape):
    """Short horizontal dashed lines that are drawn at the startpoint of the Cremona diagram 
    and after the last Force before drawing the first reaction force. 
    Are especially useful when using Force spacing option."""

    TAG = "baseline"

    LENGTH = 20
    SPACING = 20

    WIDTH = 1
    DASH = (2, 1, 1, 1)

    def __init__(self, pos: Point, diagram: TwlDiagram) -> None:
        """Create an instance of BaseLineShape."""
        super().__init__(diagram)
        self.pos = pos
        self.draw_line()

    def draw_line(self):
        """Draw the line in the diagram and store it's position and tkinter id."""
        line = self.line_coords
        self.line_tk_id = self.diagram.create_line(line.start.x, line.start.y, line.end.x, line.end.y, dash=self.DASH, tags=self.TAGS)
        self.tk_shapes[self.line_tk_id] = Polygon(line.start, line.end)

    @property
    def line_coords(self) -> Line:
        """Get the lines coordinates in the diagram."""
        return Line(Point(self.pos.x - self.LENGTH - self.SPACING, self.pos.y), Point(self.pos.x + self.LENGTH + self.SPACING, self.pos.y))


class ResultShape(ComponentShape[Force]):
    """Arrow in CremonaDiagram that represents Force calculated by solver."""

    TAG: str = "result"

    ARROW = (12,12,4)

    WIDTH: int = 2
    SELECTED_WIDTH = 3

    def __init__(self, start: Point, end: Point, force: Force, diagram: 'CremonaDiagram') -> None:
        """Create an instance of ResultShape."""
        self.start = Point(start.x, start.y)
        self.end = Point(end.x, end.y)
        super().__init__(force, diagram)
        self.diagram = diagram
        self.component = force
        self.draw_line()

    def draw_line(self):
        """Draw the line in the diagram and store the position and tkinter id."""
        self.line_tk_id = self.diagram.create_line(self.start.x, self.start.y,
                            self.end.x, self.end.y,
                            width=self.WIDTH,
                            arrow=tk.LAST, 
                            arrowshape=self.ARROW, 
                            tags=[*self.TAGS, str(self.component.id)])
        self.tk_shapes[self.line_tk_id] = Polygon(self.start, self.end)
        self.diagram.tag_raise(self.label_bg_tk_id)
        self.diagram.tag_raise(self.label_tk_id)

    @property
    def line_coords(self):
        """Get the coordinates of the shape in the diagram."""
        return Line(Point(self.start.x, self.start.y), Point(self.end.x, self.end.y))

    def is_at(self, x: float, y: float) -> bool:
        """Returns True if the shape is at the specified position in the diagram, False otherwise."""
        return Point(x, y).distance_to_line(self.line_coords) < self.WIDTH/2

    @property
    def label_position(self) -> Point:
        """Get the position of the label of this shape in the diagram. Returns the middle of the line."""
        return self.line_coords.midpoint()

    def scale(self, factor: float):
        """Scale the arrowhead of the shape to fit with current diagram scaling."""
        super().scale(factor)
        scaled_arrow = tuple(value * factor for value in self.ARROW)
        self.diagram.itemconfig(self.line_tk_id, arrowshape=scaled_arrow)


class SketchShape(ComponentShape[Force]):
    """Dashed line that represents pre-sketching a Force in cremona diagram."""

    TAG: str = "sketch"

    MIN_LENGTH = 6
    EXTEND = 40

    WIDTH = 1
    DASH = 1
    SELECTED_WIDTH = 2
    SELECTED_DASH = 10

    def __init__(self, start: Point, end: Point, force: Force, diagram: 'CremonaDiagram') -> None:
        """Create an instance of SketchShape. Calculate new end points by extending the line a bit in both directions."""
        line = Line(Point(start.x, start.y), Point(end.x, end.y))
        if line.length() < self.MIN_LENGTH:
            line = Line(Point(start.x, start.y - self.MIN_LENGTH / 2), Point(end.x, end.y + self.MIN_LENGTH / 2))
            line.rotate(start, force.angle)
        line.resize(self.EXTEND)
        self.start = line.start
        self.end = line.end
        super().__init__(force, diagram)
        self.draw_line()

    def draw_line(self):
        """Draw the sketched line in the diagram."""
        self.line_tk_id = self.diagram.create_line(self.start.x, self.start.y,
                            self.end.x, self.end.y,
                            width=self.WIDTH,
                            dash=self.DASH,
                            tags=[*self.TAGS, str(self.component.id)])
        self.tk_shapes[self.line_tk_id] = Polygon(self.start, self.end)

    @property
    def line_coords(self):
        """Get the coordinates of the line in the diagram."""
        return Line(Point(self.start.x, self.start.y), Point(self.end.x, self.end.y))

    def is_at(self, x: float, y: float) -> bool:
        """Returns True if the shape is at the specified position in the diagram, False otherwise."""
        return Point(x, y).distance_to_line(self.line_coords) < self.WIDTH/2


class CremonaDiagram(TwlDiagram):
    """Cremona diagram displayed at the right of cremona tab."""

    START_POINT = Point(800, 50)
    SCALE = 6

    def __init__(self, master, selected_step: tk.IntVar):
        """Create an instance of CremonaDiagram."""
        super().__init__(master)
        TwlApp.settings().show_cremona_labels.trace_add("write", lambda *ignore: self.update_observer())
        self.selected_step: tk.IntVar = selected_step
        self.selected_step.trace_add("write", lambda *ignore: self.display_step(self.selected_step.get()))
        self.steps = []

    def create_bottom_bar(self) -> tk.Frame:
        """Add force spacing checkbox widget to bottom of the diagram."""
        bottom_bar = super().create_bottom_bar()
        force_spacing_check = ttk.Checkbutton(bottom_bar, takefocus=False, variable=TwlApp.settings().force_spacing, text="Force Spacing", style="Custom.TCheckbutton")
        force_spacing_check.pack(padx=self.UI_PADDING)
        TwlApp.settings().force_spacing.trace_add("write", lambda *ignore: self.update_observer())
        return bottom_bar

    def update_observer(self, component_id: str="", attribute_id: str=""):
        """Update this diagram when there were changes to the Model and the solver was triggered. (By switching to cremona or result tab)
        Clears the diagram and redraws all of the lines by getting the steps from CremonaAlgorithm."""
        self.clear()
        self.steps = CremonaAlgorithm.get_steps()
        pos = self.START_POINT
        pre_sketch_pos = None
        for node, force, component, sketch in self.steps:
            existing_shape = next((shape for shape in self.component_shapes if (isinstance(shape, ResultShape) and shape.component.id == force.id)), None)
            if node and existing_shape:
                coords = self.coords(existing_shape.line_tk_id)
                pos = Point(coords[2], coords[3])
                if type(component) in (Support, Force):
                    continue
            if sketch:
                if not pre_sketch_pos:
                    pre_sketch_pos = Point(pos.x, pos.y)
            else:
                if pre_sketch_pos:
                    pos = Point(pre_sketch_pos.x, pre_sketch_pos.y)
                    pre_sketch_pos = None
            pos = self.draw_force(pos, force, component, sketch)
        if self.steps and TwlApp.settings().force_spacing.get():
            self.force_spacing()
        super().update_observer(component_id, attribute_id)
        self.display_step(self.selected_step.get())

    def draw_force(self, start: Point, force: Force, component: Component, sketch: bool) -> Point:
        """Draw or pre draw a force in the diagram."""
        angle = math.radians((force.angle + 180) % 360) if type(component) in (Support, Force) else math.radians(force.angle)
        start = Point(start.x, start.y)
        end = Point(start.x + force.strength * math.sin(angle) * self.SCALE, start.y + (-force.strength * math.cos(angle) * self.SCALE))
        if sketch:
            self.shapes.append(SketchShape(Point(start.x, start.y), Point(end.x, end.y), force, self))
        else:
            self.shapes.append(ResultShape(Point(start.x, start.y), Point(end.x, end.y), force, self))
        return Point(end.x, end.y)

    def force_spacing(self):
        """Add spacing between beam forces, external force and reaction forces in the diagram."""
        force_forces = [force for node, force, component, sketch in self.steps if not node and isinstance(component, Force)]
        [self.shapes_for(force)[0].move(BaseLineShape.SPACING, 0) for force in force_forces]
        support_forces = [force for node, force, component, sketch in self.steps if not node and isinstance(component, Support)]
        [self.shapes_for(force)[0].move(2 * BaseLineShape.SPACING, 0) for force in support_forces]
        self.shapes.append(BaseLineShape(Point(self.START_POINT.x + BaseLineShape.SPACING, self.START_POINT.y), self))
        coords = self.coords(self.find_withtag(force_forces[len(force_forces) - 1].id)[0])
        self.shapes.append(BaseLineShape(Point(coords[2], coords[3]), self))

    def display_step(self, selected_step: int):
        """Display a specific step in the cremona diagram creation. Highlights all forces on current node, highlights current force and
        hides all forces drawn after this step."""
        self.step_visibility(selected_step)
        self.step_highlighting(selected_step)

    def step_visibility(self, selected_step: int):
        """Hide all forces drawn after the selected step."""
        visible: set[Shape] = set()
        for i, step in enumerate(self.steps):
            shape_type = SketchShape if step[3] else ResultShape
            shape = self.shapes_of_type_for(shape_type, step[1])[0]
            if i <= selected_step - 1 and not (not step[3] and round(step[1].strength, 2) == 0):
                visible.add(shape)
            is_visible = shape in visible
            shape.set_visible(is_visible)
            shape.set_label_visible(is_visible and self.label_visible(shape))

    def step_highlighting(self, selected_step: int):
        """Highlights all forces on current node and current force. Also makes highlighted lines slightly thicker."""
        line_style: dict[tuple[type, bool], dict[str, Any]] = {
            #(shape type, active): line style
            (BaseLineShape, False): {"width": BaseLineShape.WIDTH, "dash": BaseLineShape.DASH},
            (ResultShape, False): {"width": ResultShape.WIDTH},
            (ResultShape, True): {"width": ResultShape.SELECTED_WIDTH},
            (SketchShape, False): {"width": SketchShape.WIDTH, "dash": SketchShape.DASH},
            (SketchShape, True): {"width": SketchShape.SELECTED_WIDTH, "dash": SketchShape.SELECTED_DASH}
        }
        for shape in self.component_shapes:
            self.highlight(shape, Colors.BLACK, line_style[(type(shape), False)])
        if 0 < selected_step < len(self.steps) + 1:
            node, force, component, sketch = self.steps[selected_step - 1]
            if node:
                for shape in self.shapes_for_node(node):
                    self.highlight(shape, Colors.SELECTED, line_style[(type(shape), True)])
            shape = self.shapes_of_type_for(SketchShape if sketch else ResultShape, force)[0]
            self.highlight(shape, Colors.DARK_SELECTED, line_style[type(shape), True])

    def highlight(self, shape: ComponentShape, color: str, line_style: dict[str, Any]):
        """Highlight a shape in the diagram with the specified color and line style."""
        for tk_id in shape.tk_shapes.keys():
            tags = self.gettags(tk_id)
            if shape.LABEL_TAG in tags:
                self.itemconfig(tk_id, fill=color)
            elif shape.LABEL_BG_TAG not in tags:
                self.itemconfig(tk_id, line_style, fill=color)

    def shapes_for_node(self, node: Node) -> list[ComponentShape]:
        """Get all shapes in the diagram that represent forces that are connected to the Node."""
        return [self.shapes_of_type_for(SketchShape if step[3] else ResultShape, step[1])[0] for step in self.steps if step[0] == node]

    def label_visible(self, shape: Shape) -> bool:
        """Return if a label should be visible for the Shape in this diagram. Labels are hidden for 0 forces and pre-sketched forces.
        Also hidden if the label option is disabled in settings."""
        return isinstance(shape, ResultShape) and round(shape.component.strength, 2) != 0 and TwlApp.settings().show_cremona_labels.get()