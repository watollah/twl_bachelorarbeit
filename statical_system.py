from typing import TypeVar, List
from twl_widget import TwlWidget
from components import *

C = TypeVar('C', bound=Component)

class ComponentList(List[C]):

    def __init__(self, widgets: list[TwlWidget]=[], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.widgets: list[TwlWidget] = widgets #Ui elements that should be updated when there is a change to this list

    def append(self, object: C) -> None:
        """Add item to the list and notify connected widgets to update"""
        super().append(object)
        self.update_widgets()

    def remove(self, value: C) -> None:
        """Remove item from the list and notify connected widgets to update"""
        super().remove(value)
        self.update_widgets()

    def update_widgets(self):
        """Update all widgets connected to this list"""
        for widget in self.widgets: widget.update()


class StaticalSystem:
    def __init__(self):
        self.nodes: ComponentList[Node] = ComponentList()
        self.beams: ComponentList[Beam] = ComponentList()
        self.supports: ComponentList[Support] = ComponentList()
        self.forces: ComponentList[Force] = ComponentList()

    def create_node(self, id: int, x: int, y: int) -> Node:
        node = Node(id, x, y)
        self.nodes.append(node)
        return node

    def create_beam(self, id: int, start_node: Node, end_node: Node) -> Beam:
        beam = Beam(id, start_node, end_node)
        self.beams.append(beam)
        return beam
    
    def create_support(self, id: int, node: Node) -> Support:
        support = Support(id, node)
        self.supports.append(support)
        return support
    
    C = TypeVar('C', bound=Component)
    @staticmethod
    def find_component_at(x: int, y: int, components: list[C]) -> C | None:
        """Checks if one of the components in the list is at the specified Coordinate"""
        return next(filter(lambda c: c.is_at(x, y), components), None)
