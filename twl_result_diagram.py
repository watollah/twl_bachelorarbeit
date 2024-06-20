from twl_app import TwlApp
from twl_math import Point, Polygon
from twl_style import Colors
from twl_components import Beam
from twl_model_diagram import ComponentShape, BeamShape
from twl_result_model_diagram import ResultModelDiagram


class ResultDiagram(ResultModelDiagram):

    def update(self) -> None:
        super().update()
        beam_forces = {force: component for force, component in TwlApp.solver().solution.items() if isinstance(component, Beam)}
        for force, component in beam_forces.items():
            strength = round(force.strength, 2)
            shapes = self.shapes_for(component)
            if strength < 0:
                color = Colors.RED
                symbol = "D"
            elif strength == 0:
                color = Colors.BLACK
                symbol = "O"
            else:
                color = Colors.DARK_SELECTED
                symbol = "Z"
            for shape in shapes:
                if isinstance(shape, BeamShape):
                    self.itemconfig(shape.label_tk_id, text=f"{component.id} - {symbol}")
                    x1, x2, y1, y2 = self.bbox(shape.label_tk_id)
                    shape.tk_shapes[shape.label_bg_tk_id] = Polygon(Point(x1, x2), Point(y1, y2))
                self.highlight(shape, color)
        self.refresh()

    def highlight(self, shape: ComponentShape, color: str):
        for tk_id in shape.tk_shapes.keys():
            tags = self.gettags(tk_id)
            if all(tag not in tags for tag in (shape.LABEL_TAG, shape.LABEL_BG_TAG)):
                self.itemconfig(tk_id, fill=color)