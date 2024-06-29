from abc import ABC, abstractmethod
import itertools
import math
from typing import Callable, TypeVar, Type, cast, Generic
from enum import Enum

import numpy as np

from c2d_math import Point, Line
from c2d_update import UpdateManager
from c2d_help import int_to_roman


C = TypeVar("C", bound='Component')
V = TypeVar("V")


class Attribute(Generic[C, V]):

    TYPE: type[V]
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

    def set_value(self, value, update: bool=True) -> tuple[bool, str]:
        """Set the value of this attribute. The value is tested for validity and cast to the attributes type."""
        filter_result = self.filter(value)
        if filter_result[0]:
            self._value = value if isinstance(value, self.TYPE) else self.TYPE(value) #type: ignore
            if update:
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


class Component(ABC):

    TAG: str = "component"

    id: AttributeDescriptor[str] = AttributeDescriptor("_id")

    def __init__(self, model: 'Model', id: str | None=None):
        self.model: Model = model
        self.attributes: list[Attribute] = []
        self._id: IdAttribute = IdAttribute(self, id)

    @classmethod
    def dummy(cls):
        """Creates a dummy instance of this Component to extract its attributes."""
        return cls(Model(UpdateManager()), id="")

    @abstractmethod
    def delete(self):
        """Deletes the component from the model and deltes components dependent on it."""

    @staticmethod
    def gen_id(i: int) -> str:
        """Generate an id based on a number i."""
        return str(i)


class IdAttribute(Attribute[Component, str]):

    TYPE = str
    ID = "id"
    NAME = "Id"
    UNIT = ""
    EDITABLE: bool = True

    def __init__(self, component: Component, value: str | None) -> None:
        super().__init__(component, value if value else "")
        if not value:
            self._value = self._component.model.next_unique_id_for(type(component))
    
    def filter(self, value) -> tuple[bool, str]:
        if hasattr(self._component, "_id") and self._component.id == value:
            return True, ""
        if value in {component.id for component in self._component.model.all_components}:
            return False, "Id already exists."
        return True, ""


class Node(Component):

    TAG: str = "node"

    x: AttributeDescriptor[float] = AttributeDescriptor("_x")
    y: AttributeDescriptor[float] = AttributeDescriptor("_y")

    def __init__(self, model: 'Model', x: float, y: float, id: str | None=None):
        super().__init__(model, id)
        self._x: XCoordinateAttribute = XCoordinateAttribute(self, x)
        self._y: YCoordinateAttribute = YCoordinateAttribute(self, y)

    @classmethod
    def dummy(cls, x: float=0, y: float=0):
        return cls(Model(UpdateManager()), x, y, id=cls.TAG)

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

    @staticmethod
    def gen_id(i: int) -> str:
        return int_to_roman(i)


class CoordinateAttribute(Attribute[Node, float]):

    TYPE = float

    def filter(self, value) -> tuple[bool, str]:
        try:
            value = float(value)
        except ValueError:
            return False, "Coordinate must be a number."
        return True, ""

    def get_display_value(self) -> str:
        return str(round(self.get_value(), 2))


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


class Beam(Component):

    TAG: str = "beam"

    start_node: AttributeDescriptor[Node] = AttributeDescriptor("_start_node")
    end_node: AttributeDescriptor[Node] = AttributeDescriptor("_end_node")
    length: AttributeDescriptor[float] = AttributeDescriptor("_length")
    angle: AttributeDescriptor[float] = AttributeDescriptor("_angle")

    def __init__(self, model: 'Model', start_node: Node, end_node: Node, id: str | None=None):
        super().__init__(model, id)
        self._start_node: StartNodeAttribute = StartNodeAttribute(self, start_node)
        self._end_node: EndNodeAttribute = EndNodeAttribute(self, end_node)
        self._length: BeamLengthAttribute = BeamLengthAttribute(self)
        self._angle: BeamAngleAttribute = BeamAngleAttribute(self)

    @classmethod
    def dummy(cls):
        return cls(Model(UpdateManager()), Node.dummy(), Node.dummy(), id=cls.TAG)

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

    @staticmethod
    def gen_id(i: int) -> str:
        return f"S{i}"


class NodeAttribute(Attribute[Component, Node]):

    TYPE = Node
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


class BeamAngleAttribute(Attribute[Beam, float]):

    TYPE = float
    ID = "angle"
    NAME = "Angle"
    UNIT = "°"
    EDITABLE: bool = True

    def __init__(self, component: Beam) -> None:
        super().__init__(component, 0)

    def filter(self, value) -> tuple[bool, str]:
        try:
            value = float(value)
        except ValueError:
            return False, "Angle must be a number."
        if not 0 <= value <= 360:
            return False, "Angle must be between 0 and 360."
        return True, ""

    def get_value(self) -> float:
        return self._component.calc_angle()

    def get_display_value(self) -> str:
        return str(round(self.get_value(), 2))

    def set_value(self, value, update: bool=True) -> tuple[bool, str]:
        filter_result = self.filter(value)
        if filter_result[0]:
            start = Point(self._component.start_node.x, self._component.start_node.y)
            end = Point(self._component.end_node.x, self._component.end_node.y)
            line = Line(start, end)
            rotate_by = (float(value) - self.get_value()) % 360
            line.rotate(start, rotate_by)
            self._component.end_node._x._value = line.end.x
            self._component.end_node._y._value = line.end.y
            if update:
                self._component.model.update_manager.notify_observers(self._component.id, self.ID)
        return filter_result


class BeamLengthAttribute(Attribute[Beam, float]):

    TYPE = float
    ID = "length"
    NAME = "Length"
    UNIT = "m"
    EDITABLE: bool = True

    def __init__(self, component: Beam) -> None:
        super().__init__(component, 0)

    def filter(self, value) -> tuple[bool, str]:
        try:
            value = float(value)
        except ValueError:
            return False, "Length must be a number."
        if not 0 < value:
            return False, "Length must be positive."
        return True, ""

    def get_value(self) -> float:
        return self._component.calc_length()

    def get_display_value(self) -> str:
        return str(round(self.get_value(), 2))

    def set_value(self, value, update: bool=True) -> tuple[bool, str]:
        filter_result = self.filter(value)
        if filter_result[0]:
            start = Point(self._component.start_node.x, self._component.start_node.y)
            end = Point(self._component.end_node.x, self._component.end_node.y)
            line = Line(start, end)
            line.set_length(float(value))
            self._component.end_node._x._value = line.end.x
            self._component.end_node._y._value = line.end.y
            if update:
                self._component.model.update_manager.notify_observers(self._component.id, self.ID)
        return filter_result


class Support(Component):

    TAG: str = "support"

    node: AttributeDescriptor[Node] = AttributeDescriptor("_node")
    angle: AttributeDescriptor[float] = AttributeDescriptor("_angle")
    constraints: AttributeDescriptor[int] = AttributeDescriptor("_constraints")

    def __init__(self, model: 'Model', node: Node, angle: float=180, constraints: int=2, id: str | None=None):
        super().__init__(model, id)
        self._node: NodeAttribute = NodeAttribute(self, node)
        self._angle: AngleAttribute = AngleAttribute(self, angle)
        self._constraints: ConstraintsAttribute = ConstraintsAttribute(self, constraints)

    @classmethod
    def dummy(cls):
        return cls(Model(UpdateManager()), Node.dummy(), id="")

    def delete(self):
        self.model.supports.remove(self)

    @staticmethod
    def gen_id(i: int) -> str:
        return chr(i + 64)


class AngleAttribute(Attribute[Component, float]):

    TYPE = float
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


class ConstraintsAttribute(Attribute[Support, int]):

    TYPE = int
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


class Force(Component):

    TAG: str = "force"

    node: AttributeDescriptor[Node] = AttributeDescriptor("_node")
    angle: AttributeDescriptor[float] = AttributeDescriptor("_angle")
    strength: AttributeDescriptor[float] = AttributeDescriptor("_strength")

    def __init__(self, model: 'Model', node: Node, angle: float=0, strength: float=1.0, id: str | None=None):
        super().__init__(model, id)
        self._node: NodeAttribute = NodeAttribute(self, node)
        self._angle: AngleAttribute = AngleAttribute(self, angle)
        self._strength: StrengthAttribute = StrengthAttribute(self, strength)

    @classmethod
    def dummy(cls, id="", node: Node | None=None, angle: float=0, strength: float=1.0):
        node = Node.dummy() if node == None else node
        dummy_force: Force = cls(Model(UpdateManager()), node, angle, strength, id=id)
        return dummy_force

    def delete(self):
        self.model.forces.remove(self)

    @staticmethod
    def gen_id(i: int) -> str:
        return f"F{i}"


class StrengthAttribute(Attribute[Force, float]):

    TYPE = float
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


class Result(Component):

    TAG: str = "result"

    force_type: AttributeDescriptor[ForceType] = AttributeDescriptor("_force_type")
    result: AttributeDescriptor[float] = AttributeDescriptor("_result")

    def __init__(self, model: 'Model', force: Force, id: str | None=None):
        super().__init__(model, id)
        self._id._value = force.id
        self._force_type: ForceTypeAttribute = ForceTypeAttribute(self, ForceType.from_value(round(force.strength, 2)))
        self._result: ResultAttribute = ResultAttribute(self, round(force.strength, 2))

    @classmethod
    def dummy(cls, force: Force | None=None, id=""):
        force = force if force else Force.dummy()
        dummy_result: Result = cls(Model(UpdateManager()), force)
        dummy_result._id._value = id
        return dummy_result

    def delete(self):
        pass


class ResultAttribute(Attribute[Result, float]):

    TYPE = float
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


class ForceTypeAttribute(Attribute[Result, ForceType]):

    TYPE = ForceType
    ID = "force_type"
    NAME = "Type"
    UNIT = ""
    EDITABLE: bool = False

    def get_display_value(self) -> str:
        return self.get_value().value


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

    def is_stat_det(self) -> bool:
        """Check if the model is statically determined and thus ready for analysis."""
        return ((2 * len(self.nodes)) - (sum(support.constraints for support in self.supports) + len(self.beams))) == 0

    def is_stable(self) -> bool:
        return not (sum(support.constraints for support in self.supports) < 3 or self.supports_parallel() or self.all_supports_intersect())

    def has_three_reaction_forces(self) -> bool:
        return sum(support.constraints for support in self.supports) == 3

    def has_overlapping_beams(self) -> bool:
        beam_to_line: Callable[[Beam], Line] = lambda beam: Line(Point(beam.start_node.x, beam.start_node.y), Point(beam.end_node.x, beam.end_node.y))
        return any(beam_to_line(b1).intersects(beam_to_line(b2)) for b1, b2 in itertools.combinations(self.beams, 2))

    def supports_parallel(self):
        if len(self.supports) > 2 and all(support.constraints == 1 for support in self.supports):
            return all(self.supports[0].angle % 180 == support.angle % 180 for support in self.supports)
        return False

    def all_supports_intersect(self):
        if not len(self.supports) == 3 or not all(support.constraints == 1 for support in self.supports) or self.supports_parallel():
            return False
        intersections = [self.support_intersection(self.supports[0], self.supports[1]),
                         self.support_intersection(self.supports[1], self.supports[2]),
                         self.support_intersection(self.supports[0], self.supports[2])]
        if any(not intersection[0] for intersection in intersections):
            return False #at least 2 supports do not intersect
        if any(intersection[0] and not intersection[1] for intersection in intersections):
            return True #2 supports are colinear -> all 3 intersect in one point
        all_x = [intersection[1].x for intersection in intersections if intersection[1]]
        all_y = [intersection[1].y for intersection in intersections if intersection[1]]
        return all(math.isclose(x, all_x[0]) for x in all_x) and all(math.isclose(y, all_y[0]) for y in all_y)

    def support_intersection(self, s1: Support, s2: Support) -> tuple[bool, Point | None]:
        if s1.angle in (90, 270) and s2.angle in (90, 270): #both horizontal
            return (True, None) if s1.node.y == s2.node.y else (False, None) #colinear or parallel
        if s1.angle in (0, 180, 360) and s2.angle in (0, 180, 360): #both vertical
            return (True, None) if s1.node.x == s2.node.x else (False, None) #colinear or parallel
        s1_m, s1_c = self.line_equation(s1)
        s2_m, s2_c = self.line_equation(s2)
        if math.isclose(s1_m, s2_m):
            if math.isclose(s1_c, s2_c):
                return True, None #colinear
            return False, None #parallel
        get_result: dict[tuple[bool, bool, bool, bool], tuple[float, float]] = {
            #s1 hor, s1 vert, s2 hor, s2 vert
            (True, False, False, True): (s2.node.x, s1.node.y),
            (False, True, True, False): (s1.node.x, s2.node.y),
            (True, False, False, False): ((s1.node.y - s2_c) / s2_m, s1.node.y),
            (False, True, False, False): (s1.node.x, s2_m * s1.node.x + s2_c),
            (False, False, True, False): ((s2.node.y - s1_c) / s1_m, s2.node.y),
            (False, False, False, True): (s2.node.x, s1_m * s2.node.x + s1_c),
            (False, False, False, False): ((s1_c - s2_c) / (s2_m - s1_m), s1_m * ((s1_c - s2_c) / (s2_m - s1_m)) + s1_c),
        }
        x, y = get_result[s1.angle in (90, 270), s1.angle in (0, 180, 360), s2.angle in (90, 270), s2.angle in (0, 180, 360)]
        return True, Point(x, y)

    def line_equation(self, support: Support):
            m = -math.tan(math.radians(support.angle))
            c = -(-support.node.y + m * support.node.x)
            return m, c

    def next_unique_id_for(self, component_type: type[C]) -> str:
        existing_ids =  {component.id for component in self.all_components}
        i = 1
        while component_type.gen_id(i) in existing_ids:
            i += 1
        return component_type.gen_id(i)


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