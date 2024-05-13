from abc import ABC, abstractmethod
from typing import Any, TypeVar, List, Type, cast
from itertools import chain

from twl_math import *
from twl_widget import *
from twl_classproperty import *


C = TypeVar('C', bound='Component')


class Component(ABC):

    TAG: str = "component"

    def __init__(self, statical_system: 'StaticalSystem'):
        self.statical_system: StaticalSystem = statical_system
        self.id: int = Component.generate_next_unique_id(statical_system.list_for_type(type(self)))

    @classmethod
    def generate_next_unique_id(cls, existing_components: list[C]):
        existing_ids = [component.id for component in existing_components]
        return next(id for id in range(1, len(existing_ids) + 2) if id not in existing_ids)

    @abstractmethod
    def delete(self):
        """Deletes the component from the statical system and deltes components dependent on it."""
        pass

    @classproperty
    @abstractmethod
    def attribute_names(cls) -> tuple:
        """Returns the names of attributes to display for the component type and get and set the attribute when editing in twl tables."""
        pass

    @property
    @abstractmethod
    def attribute_values(self) -> tuple:
        """Returns the values of attributes to display for the component type."""
        pass

    def __setattr__(self, name: str, value: Any) -> None:
        """Automatically update the connected widgets whenever one of the components attributes is changed."""
        super().__setattr__(name, value)
        if not name == "statical_system":
            self.statical_system.update_widgets()
            print(f"detected change in {self}, changed attribute: {name}")


class Node(Component):

    TAG: str = "node"

    def __init__(self, statical_system: 'StaticalSystem', x: int, y: int):
        super().__init__(statical_system)
        self.x: int = x
        self.y: int = y

    def delete(self):
        for support in self.supports: support.delete()
        for force in self.forces: force.delete()
        self.statical_system.nodes.remove(self)

    @property
    def beams(self) -> list['Beam']:
        return [beam for beam in self.statical_system.beams if beam.start_node == self or beam.end_node == self]

    @property
    def supports(self) -> list['Support']:
        return [support for support in self.statical_system.supports if support.node == self]

    @property
    def forces(self) -> list['Force']:
        return [force for force in self.statical_system.forces if force.node == self]

    @classproperty
    def attribute_names(cls) -> tuple:
        return ()

    @property
    def attribute_values(self) -> tuple:
        return ()


class Beam(Component):

    TAG: str = "beam"

    def __init__(self, statical_system: 'StaticalSystem', start_node: Node, end_node: Node):
        super().__init__(statical_system)
        self.start_node: Node = start_node
        self.end_node: Node = end_node

    def delete(self):
        self.statical_system.beams.remove(self)
        if not self.start_node.beams: self.start_node.delete()
        if not self.end_node.beams: self.end_node.delete()

    @property
    def length(self) -> float:
        p1 = Point(self.start_node.x, self.start_node.y)
        p2 = Point(self.end_node.x, self.end_node.y)
        return Line(p1, p2).length()

    @property
    def angle(self) -> float:
        p1 = Point(self.start_node.x, self.start_node.y)
        p2 = Point(self.end_node.x, self.end_node.y)
        return Line(p1, p2).angle()

    @classproperty
    def attribute_names(cls) -> tuple:
        return ("length", "angle")

    @property
    def attribute_values(self) -> tuple:
        return (round(self.length, 2), round(self.angle, 2))


class Support(Component):

    TAG: str = "support"

    def __init__(self, statical_system: 'StaticalSystem', node: Node, angle: float=0, constraints: int=2):
        super().__init__(statical_system)
        self.node: Node = node
        self.angle: float = angle
        self.constraints: int = constraints

    def delete(self):
        self.statical_system.supports.remove(self)

    @classproperty
    def attribute_names(cls) -> tuple:
        return ("angle", "constraints")

    @property
    def attribute_values(self) -> tuple:
        return (round(self.angle, 2), self.constraints)


class Force(Component):

    TAG: str = "force"

    def __init__(self, statical_system: 'StaticalSystem', node: Node, angle: float=180, strength: float=1):
        super().__init__(statical_system)
        self.node: Node = node
        self.angle: float = angle
        self.strength: float = strength

    def delete(self):
        self.statical_system.forces.remove(self)

    @classproperty
    def attribute_names(cls) -> tuple:
        return ("angle", "strength")

    @property
    def attribute_values(self) -> tuple:
        return (round(self.angle, 2), round(self.strength, 2))


class StaticalSystem:
    def __init__(self):
        self.nodes: ComponentList[Node] = ComponentList(Node, self)
        self.beams: ComponentList[Beam] = ComponentList(Beam, self)
        self.supports: ComponentList[Support] = ComponentList(Support, self)
        self.forces: ComponentList[Force] = ComponentList(Force, self)

        self.widgets: list[TwlWidget] = []

    def clear(self):
        if not self.is_empty():
            [component_list.clear() for component_list in self.component_lists]
            self.update_widgets()

    def is_empty(self) -> bool:
        return all(not component_list for component_list in self.component_lists)

    @property
    def component_lists(self):
        return (self.nodes, self.beams, self.supports, self.forces)

    @property
    def all_components(self) -> list[Component]:
        return [component for component_list in self.component_lists for component in component_list]

    def list_for_type(self, component_type: Type[C]) -> 'ComponentList[C]':
        return cast('ComponentList[C]', next(component_list for component_list in self.component_lists if component_list.component_class == component_type))

    def statically_determined(self) -> bool: #todo: implement once different types of supports have been implemented
        """Check if the system is statically determined and thus ready for analysis."""
        return False
    
    def update_widgets(self, *args):
        """Update all ui widgets connected to this statical system."""
        for widget in self.widgets: widget.update()

class ComponentList(List[C]):

    def __init__(self, component_class: Type[C], statical_system: StaticalSystem, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.component_class: Type[C] = component_class #Class of the entries in this list, to make it accessible even when the list is empty
        self.statical_system: StaticalSystem = statical_system

    def append(self, *components: C) -> None:
        """Add item to the list and notify connected widgets to update."""
        for component in components: super().append(component)
        self.statical_system.update_widgets()

    def remove(self, *components: C) -> None:
        """Remove item(s) from the list and notify connected widgets to update."""
        change: bool = False
        for component in components: 
            if component in self:
                super().remove(component)
                change = True
        if change: self.statical_system.update_widgets()

    def get_component(self, id: int) -> C | None:
        return next((component for component in self if component.id == id), None)