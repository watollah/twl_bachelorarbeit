import tkinter as tk

from c2d_app import TwlApp
from c2d_math import Point, Line, Polygon
from c2d_diagram import ComponentShape, Shape
from c2d_model_diagram import ModelDiagram, BeamShape, SupportShape, ForceShape
from c2d_components import Beam, Support, Force


class BeamForceShape(ComponentShape[Beam]):
    """Shape in result diagram that represents result force on a beam. Displayed as two arrows for tensile/compressive strength or circle for zero strength."""

    TAG: str = "beam_force"

    RADIUS = 8
    LABEL_PADDING = 20
    BORDER = 2.5

    END_OFFSET = -40
    WIDTH = 1
    D_ARROW = (12,1,10)
    Z_ARROW = (12,12,10)

    def __init__(self, beam: Beam, force: Force, diagram: 'ModelDiagram') -> None:
        """Create an instance of BeamForceShape."""
        super().__init__(beam, diagram)
        self.force = force
        if round(force.strength, 2) == 0:
            self.draw_circle()
        else:
            self.draw_arrows()

    def draw_circle(self):
        """Draw a circle on the Beam for zero force."""
        circle = self.circle_coords
        self.circle_tk_id = self.diagram.create_oval(circle[0].x, circle[0].y, circle[1].x, circle[1].y, tags=[*self.TAGS, str(self.component.id)])
        self.tk_shapes[self.circle_tk_id] = Polygon(*circle)

    @property
    def circle_coords(self) -> tuple[Point, Point]:
        """Get the coords for the zero strength force circle. Positioned in the middle of the Beam."""
        middle = self.arrow_line_coords.midpoint()
        return (Point(middle.x - self.RADIUS, middle.y - self.RADIUS), 
                Point(middle.x + self.RADIUS, middle.y + self.RADIUS))

    def draw_arrows(self):
        """Draw the arrows for compressive/tensile strength force."""
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
        """Get the coordinates of the line that the arrows are drawn on.
        The line is created behind the Beams line, with the ends slightly offset from the Nodes."""
        line = Line(Point(self.component.start_node.x, self.component.start_node.y), 
                    Point(self.component.end_node.x, self.component.end_node.y))
        line.resize(self.END_OFFSET)
        return line

    def scale(self, factor: float):
        """Scale the shape in the diagram. For zero force shape the border of the circle is scaled.
        For compressive/tensile force shape the arrowheads are scaled."""
        super().scale(factor)
        if round(self.force.strength, 2) == 0:
            self.diagram.itemconfig(self.circle_tk_id, width=self.BORDER * factor)
        else:
            arrow = self.Z_ARROW if self.force.strength < 0 else self.D_ARROW
            scaled_arrow = tuple(value * factor for value in arrow)
            self.diagram.itemconfig(self.line_tk_id, arrowshape=scaled_arrow)


class ResultModelDiagram(ModelDiagram):
    """Base class for diagrams that display Model overlayed with results from the solver. Subclassed by CremonaModelDiagram and ResultDiagram."""

    SUPPORT_FORCE_OFFSET_RANGE = 50

    def update_observer(self, component_id: str="", attribute_id: str=""):
        """Update the diagram by adding Support and Beam forces."""
        super().update_observer(component_id, attribute_id)
        self.add_support_forces()
        self.add_beam_forces()
        self.label_visibility()

    def add_support_forces(self):
        """Add Support forces to the diagram. Displayed like normal Forces as arrows next to the Supports. 
        If the arrow is overlapping with the SupportShape the arrow is automatically offset."""
        support_forces = {force: component for force, component in TwlApp.solver().solution.items() if isinstance(component, Support)}
        for force, support in support_forces.items():
            shape = ForceShape(force, self)
            self.shapes.append(shape)
            self.offset_support_force(shape, support)

    def add_beam_forces(self):
        """Add Beam forces to the diagram."""
        [shape.remove() for shape in self.shapes.copy() if isinstance(shape, BeamForceShape)]
        [self.reset_label_position(shape) for shape in self.shapes if isinstance(shape, BeamShape)]
        beam_forces = {force: component for force, component in TwlApp.solver().solution.items() if isinstance(component, Beam)}
        for force, beam in beam_forces.items():
            self.shapes.append(BeamForceShape(beam, force, self))
        self.tag_lower(BeamForceShape.TAG)

    def offset_support_force(self, shape: ForceShape, support: Support):
        """Offset Support Force arrows if they overlap with the SupportShape."""
        force = shape.component
        if support.angle - self.SUPPORT_FORCE_OFFSET_RANGE <= force.angle <= support.angle + self.SUPPORT_FORCE_OFFSET_RANGE:
            p1 = shape.arrow_coords.start
            line = Line(Point(force.node.x, force.node.y), Point(p1.x, p1.y))
            line.resize(SupportShape.HEIGHT)
            p2 = line.end
            shape.move(round(p2.x - p1.x), round(p2.y - p1.y))

    def adjust_label_positions(self):
        """Adjust the position of labels on beam with zero force shapes. 
        The circle drawn on the beam is drawn on top of the beams label, so the label is moved down slightly."""
        zero_beam_force_shapes = [shape for shape in self.shapes if isinstance(shape, BeamForceShape) and round(shape.force.strength, 2) == 0]
        for beam_force_shape in zero_beam_force_shapes:
            beam_shape = self.shapes_of_type_for(BeamShape, beam_force_shape.component)[0]
            self.reset_label_position(beam_shape)
            if self.itemcget(beam_force_shape.circle_tk_id, "state") in ("", tk.NORMAL):
                beam_shape.tk_shapes[beam_shape.label_tk_id].move(0, BeamForceShape.RADIUS + BeamForceShape.LABEL_PADDING)
                beam_shape.tk_shapes[beam_shape.label_bg_tk_id].move(0, BeamForceShape.RADIUS + BeamForceShape.LABEL_PADDING)

    def reset_label_position(self, beam_shape: BeamShape):
        """Reset the position of Beam labels to their default position."""
        label_pos = beam_shape.label_position
        current_pos = beam_shape.tk_shapes[beam_shape.label_tk_id].points[0]
        delta_x = label_pos.x - current_pos.x
        delta_y = label_pos.y - current_pos.y
        beam_shape.tk_shapes[beam_shape.label_tk_id].move(delta_x, delta_y)
        beam_shape.tk_shapes[beam_shape.label_bg_tk_id].move(delta_x, delta_y)

    def label_visible(self, shape: Shape) -> bool:
        """Returns if label should be visible for shape in diagram. Labels for SupportShapes and BeamForceShapes are disabled.
        SupportShape labels are not necessary in this diagram because the Support is labeled by it's reaction forces."""
        return type(shape) not in (SupportShape, BeamForceShape) and super().label_visible(shape)