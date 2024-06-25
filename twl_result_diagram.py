import math

from twl_app import TwlApp
from twl_math import Point, Line, Polygon
from twl_style import Colors
from twl_components import Beam, Force
from twl_diagram import Shape
from twl_model_diagram import ComponentShape
from twl_result_model_diagram import ResultModelDiagram


class BeamForcePlotShape(ComponentShape[Beam]):

    TAG: str = "beam_force_plot"

    MAX_HEIGHT = 40
    BORDER = 1

    def __init__(self, beam: Beam, force: Force, diagram: 'ResultModelDiagram') -> None:
        super().__init__(beam, diagram)
        self.force = force
        rect = self.rect_coords()
        bd_color, bg_color = (Colors.DARK_SELECTED, Colors.LIGHT_SELECTED) if force.strength < 0 else (Colors.RED, Colors.LIGHT_RED)
        self.rect_id = self.diagram.create_polygon(rect[0].x, rect[0].y, rect[1].x, rect[1].y,
                            rect[2].x, rect[2].y, rect[3].x, rect[3].y,
                            width=self.BORDER,
                            outline=bd_color,
                            fill=bg_color,
                            tags=[*self.TAGS, str(self.component.id)])
        self.tk_shapes[self.rect_id] = Polygon(rect[0], rect[1], rect[2], rect[3])
        self.set_label_visible(False)

    def rect_coords(self) -> tuple[Point, Point, Point, Point]:
        p1 = Point(self.component.start_node.x, self.component.start_node.y)
        p2 = Point(self.component.end_node.x, self.component.end_node.y)
        line = Line(Point(p1.x, p1.y), Point(p2.x, p2.y))
        height = (self.force.strength / self.get_max_strength()) * self.MAX_HEIGHT
        angle = (self.component.angle + 90) % 360
        if 0 <= angle <= 90 or 270 < angle <= 360:
            angle = (angle + 180) % 360
        angle = math.radians(angle)
        line.move(int(math.sin(angle) * height), -1 * int(math.cos(angle) * height))
        return p1, p2, line.end, line.start

    def get_max_strength(self) -> float:
        return max([force.strength for force, component in TwlApp.solver().solution.items() if isinstance(component, Beam)])

    def scale(self, factor: float):
        super().scale(factor)
        self.diagram.itemconfig(self.rect_id, width=self.BORDER * factor)


class ResultDiagram(ResultModelDiagram):

    def update_observer(self, component_id: str="", attribute_id: str=""):
        super().update_observer(component_id, attribute_id)
        beam_forces = {force: component for force, component in TwlApp.solver().solution.items() if isinstance(component, Beam)}
        for force, beam in beam_forces.items():
            strength = round(force.strength, 2)
            if not strength == 0:
                color = Colors.DARK_SELECTED if strength < 0 else Colors.RED
                for shape in self.shapes_for(beam):
                    self.highlight(shape, color)
                self.shapes.append(BeamForcePlotShape(beam, force, self))
        self.adjust_label_positions()
        self.tag_lower(BeamForcePlotShape.TAG)
        self.refresh()

    def highlight(self, shape: ComponentShape, color: str):
        for tk_id in shape.tk_shapes.keys():
            tags = self.gettags(tk_id)
            if all(tag not in tags for tag in (shape.LABEL_TAG, shape.LABEL_BG_TAG)):
                self.itemconfig(tk_id, fill=color)

    def label_visible(self, shape: Shape) -> bool:
        return type(Shape) != BeamForcePlotShape and super().label_visible(shape)