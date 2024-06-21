from twl_app import TwlApp
from twl_math import Point, Polygon
from twl_style import Colors
from twl_components import Beam
from twl_model_diagram import ComponentShape, BeamShape
from twl_result_model_diagram import ResultModelDiagram, BeamForceShape


class ResultDiagram(ResultModelDiagram):

    def update(self) -> None:
        super().update()
        beam_forces = {force: component for force, component in TwlApp.solver().solution.items() if isinstance(component, Beam)}
        for force, component in beam_forces.items():
            strength = round(force.strength, 2)
            if not strength == 0:
                color = Colors.RED if strength < 0 else Colors.DARK_SELECTED
                for shape in self.shapes_for(component):
                    self.highlight(shape, color)
        self.adjust_label_positions()
        self.refresh()

    def highlight(self, shape: ComponentShape, color: str):
        for tk_id in shape.tk_shapes.keys():
            tags = self.gettags(tk_id)
            if all(tag not in tags for tag in (shape.LABEL_TAG, shape.LABEL_BG_TAG)):
                self.itemconfig(tk_id, fill=color)