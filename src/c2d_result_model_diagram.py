import tkinter as tk

from c2d_app import TwlApp
from c2d_math import Point, Line, Polygon
from c2d_diagram import ComponentShape, Shape
from c2d_model_diagram import ModelDiagram, BeamShape, SupportShape, ForceShape
from c2d_components import Beam, Support, Force


class BeamForceShape(ComponentShape[Beam]):

    TAG: str = "beam_force"

    RADIUS = 8
    LABEL_PADDING = 20
    BORDER = 2.5

    END_OFFSET = -40
    WIDTH = 1
    D_ARROW = (12,1,10)
    Z_ARROW = (12,12,10)

    def __init__(self, beam: Beam, force: Force, diagram: 'ModelDiagram') -> None:
        super().__init__(beam, diagram)
        self.force = force
        if round(force.strength, 2) == 0:
            self.draw_circle()
        else:
            self.draw_arrows()

    def draw_circle(self):
            circle = self.circle_coords
            self.circle_tk_id = self.diagram.create_oval(circle[0].x, circle[0].y, circle[1].x, circle[1].y, tags=[*self.TAGS, str(self.component.id)])
            self.tk_shapes[self.circle_tk_id] = Polygon(*circle)

    @property
    def circle_coords(self) -> tuple[Point, Point]:
        middle = self.arrow_line_coords.midpoint()
        return (Point(middle.x - self.RADIUS, middle.y - self.RADIUS), 
                Point(middle.x + self.RADIUS, middle.y + self.RADIUS))

    def draw_arrows(self):
            line = self.arrow_line_coords
            self.line_tk_id = self.diagram.create_line(line.start.x, line.start.y,
                                line.end.x, line.end.y,
                                width=self.WIDTH,
                                arrow=tk.BOTH, 
                                arrowshape=self.Z_ARROW if self.force.strength < 0 else self.D_ARROW, 
                                tags=[*self.TAGS, str(self.component.id)])
            self.tk_shapes[self.line_tk_id] = Polygon(line.start, line.end)

    @property
    def arrow_line_coords(self):
        line = Line(Point(self.component.start_node.x, self.component.start_node.y), 
                    Point(self.component.end_node.x, self.component.end_node.y))
        line.resize(self.END_OFFSET)
        return line

    def scale(self, factor: float):
        super().scale(factor)
        if round(self.force.strength, 2) == 0:
            self.diagram.itemconfig(self.circle_tk_id, width=self.BORDER * factor)
        else:
            arrow = self.Z_ARROW if self.force.strength < 0 else self.D_ARROW
            scaled_arrow = tuple(value * factor for value in arrow)
            self.diagram.itemconfig(self.line_tk_id, arrowshape=scaled_arrow)


class ResultModelDiagram(ModelDiagram):

    SUPPORT_FORCE_OFFSET_RANGE = 50

    def update_observer(self, component_id: str="", attribute_id: str=""):
        super().update_observer(component_id, attribute_id)
        self.add_support_forces()
        self.add_beam_forces()
        self.label_visibility()

    def add_support_forces(self):
        support_forces = {force: component for force, component in TwlApp.solver().solution.items() if isinstance(component, Support)}
        for force, support in support_forces.items():
            shape = ForceShape(force, self)
            self.shapes.append(shape)
            self.offset_support_force(shape, support)

    def add_beam_forces(self):
        [shape.remove() for shape in self.shapes.copy() if isinstance(shape, BeamForceShape)]
        [self.reset_label_position(shape) for shape in self.shapes if isinstance(shape, BeamShape)]
        beam_forces = {force: component for force, component in TwlApp.solver().solution.items() if isinstance(component, Beam)}
        for force, beam in beam_forces.items():
            self.shapes.append(BeamForceShape(beam, force, self))
        self.tag_lower(BeamForceShape.TAG)

    def offset_support_force(self, shape: ForceShape, support: Support):
        force = shape.component
        if support.angle - self.SUPPORT_FORCE_OFFSET_RANGE <= force.angle <= support.angle + self.SUPPORT_FORCE_OFFSET_RANGE:
            p1 = shape.arrow_coords.start
            line = Line(Point(force.node.x, force.node.y), Point(p1.x, p1.y))
            line.resize(SupportShape.HEIGHT)
            p2 = line.end
            shape.move(round(p2.x - p1.x), round(p2.y - p1.y))

    def adjust_label_positions(self):
        zero_beam_force_shapes = [shape for shape in self.shapes if isinstance(shape, BeamForceShape) and round(shape.force.strength, 2) == 0]
        for beam_force_shape in zero_beam_force_shapes:
            beam_shape = self.shapes_of_type_for(BeamShape, beam_force_shape.component)[0]
            self.reset_label_position(beam_shape)
            if self.itemcget(beam_force_shape.circle_tk_id, "state") in ("", tk.NORMAL):
                beam_shape.tk_shapes[beam_shape.label_tk_id].move(0, BeamForceShape.RADIUS + BeamForceShape.LABEL_PADDING)
                beam_shape.tk_shapes[beam_shape.label_bg_tk_id].move(0, BeamForceShape.RADIUS + BeamForceShape.LABEL_PADDING)

    def reset_label_position(self, beam_shape: BeamShape):
        label_pos = beam_shape.label_position
        current_pos = beam_shape.tk_shapes[beam_shape.label_tk_id].points[0]
        delta_x = label_pos.x - current_pos.x
        delta_y = label_pos.y - current_pos.y
        beam_shape.tk_shapes[beam_shape.label_tk_id].move(delta_x, delta_y)
        beam_shape.tk_shapes[beam_shape.label_bg_tk_id].move(delta_x, delta_y)

    def label_visible(self, shape: Shape) -> bool:
        return type(shape) not in (SupportShape, BeamForceShape) and super().label_visible(shape)