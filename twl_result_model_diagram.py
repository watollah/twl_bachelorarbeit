import tkinter as tk

from twl_app import TwlApp
from twl_math import Point, Line, Polygon
from twl_diagram import ComponentShape, Shape
from twl_model_diagram import ModelDiagram, SupportShape, ForceShape
from twl_components import Beam, Support, Force


class BeamForceShape(ComponentShape[Beam]):

    TAG: str = "beam_force"

    END_OFFSET = -40
    WIDTH = 1
    D_ARROW = (12,1,10)
    Z_ARROW = (12,12,10)

    def __init__(self, beam: Beam, force: Force, diagram: 'ModelDiagram') -> None:
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


class ResultModelDiagram(ModelDiagram):

    SUPPORT_FORCE_OFFSET_RANGE = 50

    def update(self) -> None:
        super().update()
        self.add_support_forces()
        self.add_beam_forces()
        self.refresh()

    def add_support_forces(self):
        support_forces = {force: component for force, component in TwlApp.solver().solution.items() if isinstance(component, Support)}
        for force, support in support_forces.items():
            shape = ForceShape(force, self)
            self.shapes.append(shape)
            self.offset_support_force(shape, support)

    def add_beam_forces(self):
        beam_forces = {force: component for force, component in TwlApp.solver().solution.items() if isinstance(component, Beam)}
        for force, beam in beam_forces.items():
            if not round(force.strength, 2) == 0:
                self.shapes.append(BeamForceShape(beam, force, self))
        self.tag_lower(BeamForceShape.TAG)

    def offset_support_force(self, shape: ForceShape, support: Support):
        force = shape.component
        if support.angle - self.SUPPORT_FORCE_OFFSET_RANGE <= force.angle <= support.angle + self.SUPPORT_FORCE_OFFSET_RANGE:
            p1 = shape.arrow_coords().start
            line = Line(Point(force.node.x, force.node.y), Point(p1.x, p1.y))
            line.resize(SupportShape.HEIGHT)
            p2 = line.end
            shape.move(p2.x - p1.x, p2.y - p1.y)

    def label_visible(self, shape_type: type[Shape]) -> bool:
        return shape_type not in (SupportShape, BeamForceShape) and super().label_visible(shape_type)