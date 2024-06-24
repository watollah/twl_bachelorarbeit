from abc import ABC, abstractmethod
from typing import TypeVar, Type, cast, Generic
from enum import Enum

from twl_math import Point, Line
from twl_update import UpdateManager
from twl_help import int_to_roman


C = TypeVar("C", bound='Component')
V = TypeVar("V")

class Attribute(Generic[C, V]):

    ID: str = ""
    NAME: str = ""
    UNIT: str = ""
    EDITABLE: bool = False

    def __init__(self, component: C, value: V) -> None:
        self._component: C = component
        self._value: V = value
        component.attributes.append(self)

    def get_value(self) -> V:
        return self._value

    def set_value(self, value) -> tuple[bool, str]:
        """Set the value of this attribute. The value is tested for validity and cast to the attributes type."""
        filter_result = self.filter(value)
        if filter_result[0]:
            self._value = type(self._value)(value) #type: ignore
            self._component.model.update_manager.notify_observers(self._component.id, self.ID)
            print(f"detected change in {self._component}, changed attribute: {self.NAME}")
        return filter_result

    def filter(self, value) -> tuple[bool, str]:
        """Test if a value is valid for this attribute. If valid, it returns True and an empty String.
        If not valid, it returns False and an explanation."""
        return True, ""

    @property
    def description(self) -> str:
        return self.NAME + (f" (in {self.UNIT})" if self.UNIT != "" else "")

    def get_display_value(self) -> str:
        return str(self.get_value())


class AttributeDescriptor(Generic[V]):

    def __init__(self, attr_name: str):
        self.attr_name: str = attr_name

    def __get__(self, instance, owner) -> V:
        return getattr(instance, self.attr_name).get_value()

    def __set__(self, instance, value: V) -> tuple[bool, str]:
        return getattr(instance, self.attr_name).set_value(value)

    # def set(self, value: V) -> tuple[bool, str]:
    #     getattr(instance??, self.attr_name).set_value(value)


class IdAttribute(Attribute['Component', str]):

    ID = "id"
    NAME = "Id"
    UNIT = ""
    EDITABLE: bool = True

    def __init__(self, component: 'Component') -> None:
        super().__init__(component, "")
        self._value = self._generate_next_unique_id()

    def filter(self, value) -> tuple[bool, str]:
        if hasattr(self._component, "_id") and self._component.id == value:
            return True, ""
        if value in {component.id for component in self._component.model.all_components}:
            return False, "Id already exists."
        return True, ""

    def _generate_next_unique_id(self) -> str:
        i = 1
        while not self.filter(self._component.gen_id(i))[0]:
            i += 1
        return self._component.gen_id(i)


class CoordinateAttribute(Attribute['Component', int]):

    def filter(self, value) -> tuple[bool, str]:
        try:
            value = int(value)
        except ValueError:
            return False, "Coordinate must be a number."
        return True, ""


class XCoordinateAttribute(CoordinateAttribute):

    ID = "x"
    NAME = "X"
    UNIT = ""
    EDITABLE: bool = True


class YCoordinateAttribute(CoordinateAttribute):

    ID = "y"
    NAME = "Y"
    UNIT = ""
    EDITABLE: bool = True


class NodeAttribute(Attribute['Component', 'Node']):

    ID = "node"
    NAME = "Node"
    UNIT = ""
    EDITABLE: bool = False

    def get_display_value(self) -> str:
        return self._value.id


class StartNodeAttribute(NodeAttribute):

    ID = "startnode"
    NAME = "Start"
    UNIT = ""
    EDITABLE: bool = False


class EndNodeAttribute(NodeAttribute):

    ID = "endnode"
    NAME = "End"
    UNIT = ""
    EDITABLE: bool = False


class AngleAttribute(Attribute['Component', float]):

    ID = "angle"
    NAME = "Angle"
    UNIT = "°"
    EDITABLE: bool = True

    def filter(self, value) -> tuple[bool, str]:
        try:
            value = float(value)
        except ValueError:
            return False, "Angle must be a number."
        if not 0 <= value <= 360:
            return False, "Angle must be between 0 and 360."
        return True, ""

    def get_display_value(self) -> str:
        return str(round(self.get_value(), 2))


class BeamAngleAttribute(Attribute['Beam', float]):

    ID = "angle"
    NAME = "Angle"
    UNIT = "°"
    EDITABLE: bool = False

    def __init__(self, component: 'Beam') -> None:
        super().__init__(component, 0)

    def get_value(self) -> float:
        return self._component.calc_angle()

    def get_display_value(self) -> str:
        return str(round(self.get_value(), 2))


class BeamLengthAttribute(Attribute['Beam', float]):

    ID = "length"
    NAME = "Length"
    UNIT = "m"
    EDITABLE: bool = False

    def __init__(self, component: 'Beam') -> None:
        super().__init__(component, 0)

    def get_value(self) -> float:
        return self._component.calc_length()

    def get_display_value(self) -> str:
        return str(round(self.get_value(), 2))


class ConstraintsAttribute(Attribute['Support', int]):

    ID = "constraints"
    NAME = "Constraints"
    UNIT = ""
    EDITABLE: bool = True

    def filter(self, value) -> tuple[bool, str]:
        try:
            value = int(value)
        except ValueError:
            return False, "Must be 1 or 2."
        if not value in {1, 2}:
            return False, "Must be 1 or 2."
        return True, ""


class StrengthAttribute(Attribute['Force', float]):

    ID = "strength"
    NAME = "Strength"
    UNIT = "kN"
    EDITABLE: bool = True

    def filter(self, value) -> tuple[bool, str]:
        try:
            value = float(value)
        except ValueError:
            return False, "Strength must be a number."
        return True, ""


class ResultAttribute(Attribute['Result', float]):

    ID = "result"
    NAME = "Strength"
    UNIT = "kN"
    EDITABLE: bool = False

    def filter(self, value) -> tuple[bool, str]:
        try:
            value = float(value)
        except ValueError:
            return False, "Result must be a number."
        return True, ""

    def get_display_value(self) -> str:
        return str(0.0 if self.get_value() == 0 else self.get_value())


class ForceType(Enum):

    COMPRESSIVE = "C"
    ZERO = "0"
    TENSILE = "T"

    @classmethod
    def from_value(cls, value: float):
        if value < 0:
            return cls.COMPRESSIVE
        elif value == 0:
            return cls.ZERO
        else:
            return cls.TENSILE


class ForceTypeAttribute(Attribute['Result', ForceType]):

    ID = "force_type"
    NAME = "Type"
    UNIT = ""
    EDITABLE: bool = False

    def get_display_value(self) -> str:
        return self.get_value().value


class Component(ABC):

    TAG: str = "component"

    id: AttributeDescriptor[str] = AttributeDescriptor("_id")

    def __init__(self, model: 'Model'):
        self.model: Model = model
        self.attributes: list[Attribute] = []
        self._id: IdAttribute = IdAttribute(self)

    @classmethod
    def dummy(cls):
        """Creates a dummy instance of this Component to extract its attributes."""
        return cls(Model(UpdateManager()))

    @abstractmethod
    def delete(self):
        """Deletes the component from the model and deltes components dependent on it."""

    def gen_id(self, i: int) -> str:
        """Generate an id based on a number i."""
        return str(i)


class Node(Component):

    TAG: str = "node"

    x: AttributeDescriptor[int] = AttributeDescriptor("_x")
    y: AttributeDescriptor[int] = AttributeDescriptor("_y")

    def __init__(self, model: 'Model', x: int, y: int):
        super().__init__(model)
        self._x: XCoordinateAttribute = XCoordinateAttribute(self, x)
        self._y: YCoordinateAttribute = YCoordinateAttribute(self, y)

    @classmethod
    def dummy(cls):
        return cls(Model(UpdateManager()), 0, 0)

    def delete(self):
        for support in self.supports: support.delete()
        for force in self.forces: force.delete()
        self.model.nodes.remove(self)

    @property
    def beams(self) -> list['Beam']:
        return [beam for beam in self.model.beams if beam.start_node == self or beam.end_node == self]

    @property
    def supports(self) -> list['Support']:
        return [support for support in self.model.supports if support.node == self]

    @property
    def forces(self) -> list['Force']:
        return [force for force in self.model.forces if force.node == self]

    def gen_id(self, i: int) -> str:
        return int_to_roman(i)


class Beam(Component):

    TAG: str = "beam"

    start_node: AttributeDescriptor[Node] = AttributeDescriptor("_start_node")
    end_node: AttributeDescriptor[Node] = AttributeDescriptor("_end_node")
    length: AttributeDescriptor[float] = AttributeDescriptor("_length")
    angle: AttributeDescriptor[float] = AttributeDescriptor("_angle")

    def __init__(self, model: 'Model', start_node: Node, end_node: Node):
        super().__init__(model)
        self._start_node: StartNodeAttribute = StartNodeAttribute(self, start_node)
        self._end_node: EndNodeAttribute = EndNodeAttribute(self, end_node)
        self._length: BeamLengthAttribute = BeamLengthAttribute(self)
        self._angle: BeamAngleAttribute = BeamAngleAttribute(self)

    @classmethod
    def dummy(cls):
        return cls(Model(UpdateManager()), Node.dummy(), Node.dummy())

    def delete(self):
        self.model.beams.remove(self)
        if not self.start_node.beams: self.start_node.delete()
        if not self.end_node.beams: self.end_node.delete()

    def calc_length(self) -> float:
        p1 = Point(self.start_node.x, self.start_node.y)
        p2 = Point(self.end_node.x, self.end_node.y)
        return Line(p1, p2).length_scaled()

    def calc_angle(self) -> float:
        p1 = Point(self.start_node.x, self.start_node.y)
        p2 = Point(self.end_node.x, self.end_node.y)
        return Line(p1, p2).angle()

    def gen_id(self, i: int) -> str:
        return f"S{i}"


class Support(Component):

    TAG: str = "support"

    node: AttributeDescriptor[Node] = AttributeDescriptor("_node")
    angle: AttributeDescriptor[float] = AttributeDescriptor("_angle")
    constraints: AttributeDescriptor[int] = AttributeDescriptor("_constraints")

    def __init__(self, model: 'Model', node: Node, angle: float=180, constraints: int=2):
        super().__init__(model)
        self._node: NodeAttribute = NodeAttribute(self, node)
        self._angle: AngleAttribute = AngleAttribute(self, angle)
        self._constraints: ConstraintsAttribute = ConstraintsAttribute(self, constraints)

    @classmethod
    def dummy(cls):
        return cls(Model(UpdateManager()), Node.dummy())

    def delete(self):
        self.model.supports.remove(self)

    def gen_id(self, i: int) -> str:
        return chr(i + 64)


class Force(Component):

    TAG: str = "force"

    node: AttributeDescriptor[Node] = AttributeDescriptor("_node")
    angle: AttributeDescriptor[float] = AttributeDescriptor("_angle")
    strength: AttributeDescriptor[float] = AttributeDescriptor("_strength")

    def __init__(self, model: 'Model', node: Node, angle: float=0, strength: float=1.0):
        super().__init__(model)
        self._node: NodeAttribute = NodeAttribute(self, node)
        self._angle: AngleAttribute = AngleAttribute(self, angle)
        self._strength: StrengthAttribute = StrengthAttribute(self, strength)

    @classmethod
    def dummy(cls, id: str="dummy_force", node: Node | None=None, angle: float=0, strength: float=1.0):
        node = Node.dummy() if node == None else node
        dummy_force: Force = cls(Model(UpdateManager()), node, angle, strength)
        dummy_force.id = id
        return dummy_force

    def delete(self):
        self.model.forces.remove(self)

    def gen_id(self, i: int) -> str:
        return f"F{i}"


class Result(Component):

    TAG: str = "result"

    force_type: AttributeDescriptor[ForceType] = AttributeDescriptor("_force_type")
    result: AttributeDescriptor[float] = AttributeDescriptor("_result")

    def __init__(self, model: 'Model', force: Force):
        super().__init__(model)
        self.id = force.id
        self._force_type: ForceTypeAttribute = ForceTypeAttribute(self, ForceType.from_value(round(force.strength, 2)))
        self._result: ResultAttribute = ResultAttribute(self, round(force.strength, 2))

    @classmethod
    def dummy(cls, id: str="dummy_result", force: Force | None=None):
        force = force if force else Force.dummy()
        dummy_result: Result = cls(Model(UpdateManager()), force)
        dummy_result.id = id
        return dummy_result

    def delete(self):
        pass

class Model:
    def __init__(self, update_manager: UpdateManager):
        self.nodes: ComponentList[Node] = ComponentList(Node, update_manager)
        self.beams: ComponentList[Beam] = ComponentList(Beam, update_manager)
        self.supports: ComponentList[Support] = ComponentList(Support, update_manager)
        self.forces: ComponentList[Force] = ComponentList(Force, update_manager)

        self.update_manager: UpdateManager = update_manager

    def clear(self):
        if not self.is_empty():
            [component_list.clear() for component_list in self.component_lists]
        self.update_manager.notify_observers()

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

    def statically_determined(self) -> bool:
        """Check if the model is statically determined and thus ready for analysis."""
        return ((2 * len(self.nodes)) - (sum(support.constraints for support in self.supports) + len(self.beams))) == 0


class ComponentList(list[C]):

    def __init__(self, component_class: Type[C], update_manager: UpdateManager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.component_class: Type[C] = component_class #Class of the entries in this list, to make it accessible even when the list is empty
        self.update_manager: UpdateManager = update_manager

    def append(self, *components: C) -> None:
        """Add item to the list and notify connected widgets to update."""
        for component in components: super().append(component)
        self.update_manager.notify_observers()

    def remove(self, *components: C) -> None:
        """Remove item(s) from the list and notify connected widgets to update."""
        [super().remove(component) for component in components if component in self]
        self.update_manager.notify_observers()

    def component_for_id(self, id: str) -> C | None:
        return next((component for component in self if component.id == id), None)