import math

from c2d_app import TwlApp
from c2d_math import Point, Line, Polygon
from c2d_style import Colors
from c2d_components import Beam, Force
from c2d_diagram import Shape
from c2d_model_diagram import ComponentShape
from c2d_result_model_diagram import BeamForceShape, ResultModelDiagram


class BeamForcePlotShape(ComponentShape[Beam]):
    """Plotted result force in the result diagram. Displayed as rectangles on the Beams."""

    TAG: str = "beam_force_plot"

    MAX_HEIGHT = 40
    BORDER = 1

    def __init__(self, beam: Beam, force: Force, diagram: 'ResultModelDiagram') -> None:
        """Create an instance of BeamForcePlotShape."""
        super().__init__(beam, diagram)
        self.force = force
        self.draw_rect()

    def draw_rect(self):
        """Draw the rectangle shape and store its coordinates and tkinter id."""
        rect = self.rect_coords
        bd_color, bg_color = (Colors.DARK_SELECTED, Colors.LIGHT_SELECTED) if self.force.strength < 0 else (Colors.RED, Colors.LIGHT_RED)
        self.rect_tk_id = self.diagram.create_polygon(rect[0].x, rect[0].y, rect[1].x, rect[1].y,
                            rect[2].x, rect[2].y, rect[3].x, rect[3].y,
                            width=self.BORDER,
                            outline=bd_color,
                            fill=bg_color,
                            tags=[*self.TAGS, str(self.component.id)])
        self.tk_shapes[self.rect_tk_id] = Polygon(rect[0], rect[1], rect[2], rect[3])

    @property
    def rect_coords(self) -> tuple[Point, Point, Point, Point]:
        """Calculate the coordinates of the rectangle. The orientation is determined by the strength being compressive or tensile.
        The maximum height of the rectangle is fixed and assigned to the biggest force in the result. The rest of the heights are calculated
        as fractions of the maximum height."""
        p1 = Point(self.component.start_node.x, self.component.start_node.y)
        p2 = Point(self.component.end_node.x, self.component.end_node.y)
        line = Line(Point(p1.x, p1.y), Point(p2.x, p2.y))
        height = 0 if self.get_max_strength() == 0 or round(self.force.strength, 2) == 0 else (self.force.strength / self.get_max_strength()) * self.MAX_HEIGHT
        angle = (self.component.angle + 90) % 360
        if 0 <= angle <= 90 or 270 < angle <= 360:
            angle = (angle + 180) % 360
        angle = math.radians(angle)
        line.move(int(math.sin(angle) * height), -1 * int(math.cos(angle) * height))
        return p1, p2, line.end, line.start

    def get_max_strength(self) -> float:
        """Get the maximum result force strength in the diagram."""
        return max([abs(force.strength) for force, component in TwlApp.solver().solution.items() if isinstance(component, Beam)])

    def scale(self, factor: float):
        """Scale the width of the rectangle border."""
        super().scale(factor)
        self.diagram.itemconfig(self.rect_tk_id, width=self.BORDER * factor)


class ResultDiagram(ResultModelDiagram):
    """Result diagram displayed in result tab. Displays to the user the result of solving the Model.
    Shows the beams marked with symbols and colors as compressive/tensile/zero and the forces on the beams plotted as rectangles."""

    def update_observer(self, component_id: str="", attribute_id: str=""):
        """Update the diagram by redrawing the BeamForcePlotShapes."""
        super().update_observer(component_id, attribute_id)
        [shape.remove() for shape in self.shapes.copy() if isinstance(shape, BeamForcePlotShape)]
        self.draw_beam_force_plots()
        self.adjust_label_positions()
        self.refresh()

    def draw_beam_force_plots(self):
        """Draw the result in the diagram for each beam."""
        beam_forces = {force: component for force, component in TwlApp.solver().solution.items() if isinstance(component, Beam)}
        for force, beam in beam_forces.items():
            strength = round(force.strength, 2)
            color = Colors.BLACK if strength == 0 else Colors.DARK_SELECTED if strength < 0 else Colors.RED
            for shape in self.shapes_for(beam):
                self.highlight(shape, color)
            self.shapes.append(BeamForcePlotShape(beam, force, self))
        self.tag_lower(BeamForcePlotShape.TAG)

    def highlight(self, shape: ComponentShape, color: str):
        """Highlight a shape in the diagram with the specified color."""
        for tk_id in shape.tk_shapes.keys():
            tags = self.gettags(tk_id)
            if all(tag not in tags for tag in (shape.LABEL_TAG, shape.LABEL_BG_TAG)):
                self.itemconfig(tk_id, fill=color)
        if isinstance(shape, BeamForceShape) and round(shape.force.strength, 2) == 0:
            self.itemconfig(shape.circle_tk_id, fill=Colors.WHITE)

    def label_visible(self, shape: Shape) -> bool:
        """Returns if label for shape should be visible in the diagram. Labels are disabled for BeamForceShapes and BeamForcePlotShapes."""
        return type(shape) not in (BeamForceShape, BeamForcePlotShape) and super().label_visible(shape)