from twl_style import Colors
from twl_diagram import ComponentShape
from twl_components import Component, Node, Force
from twl_cremona_algorithm import CremonaAlgorithm
from twl_model_diagram import ModelDiagram, NodeShape, SupportShape


class CremonaModelDiagram(ModelDiagram):

    def __init__(self, master):
        super().__init__(master)
        self.steps: list[tuple[Node | None, Force, Component, bool]] = []

    def update(self) -> None:
        super().update()
        self.steps = CremonaAlgorithm.get_steps()

    def display_step(self, selected_step: int):
        for shape in self.get_component_shapes():
            self.highlight(shape, Colors.BLACK, Colors.WHITE)
        if 0 < selected_step < len(self.steps) + 1:
            node, force, component, sketch = self.steps[selected_step - 1]
            if node:
                self.highlight(self.shape_for(node), Colors.DARK_SELECTED, Colors.SELECTED)
                for shape in self.shapes_for_node(force.node):
                    self.highlight(shape, Colors.SELECTED, Colors.WHITE)
            current_shape = self.shape_for(component)
            self.highlight(current_shape, Colors.DARK_SELECTED, Colors.SELECTED)

    def shapes_for_node(self, node: Node):
        return [self.shape_for(step[2]) for step in self.steps if step[0] == node]

    def highlight(self, shape: ComponentShape, color: str, bg_color: str):
        for tk_id in shape.tk_shapes.keys():
            tags = self.gettags(tk_id)
            if shape.LABEL_TAG in tags:
                self.itemconfig(tk_id, fill=color)
            elif shape.LABEL_BG_TAG not in tags:
                if any(tag in tags for tag in (NodeShape.TAG, SupportShape.TAG)) and not SupportShape.LINE_TAG in tags:
                    self.itemconfig(tk_id, outline=color, fill=bg_color)
                else:
                    self.itemconfig(tk_id, fill=color)