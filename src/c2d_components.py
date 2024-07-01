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
    """Represents an attribute of a component. Stores a value of a specific type and provides more information and functionality around it.
    Handles validation and notifying Observers to update UI components on changes. Provides extra information like unit, description and display value to
    represent the attribute in the UI."""

    TYPE: type[V]
    ID: str = ""
    NAME: str = ""
    UNIT: str = ""
    EDITABLE: bool = False

    def __init__(self, component: C, value: V) -> None:
        """Create an instance of Attribute."""
        self._component: C = component
        self._value: V = value
        component.attributes.append(self)

    def get_value(self) -> V:
        """Returns the Attribute's value."""
        return self._value

    def set_value(self, value, update: bool=True) -> tuple[bool, str]:
        """Set the value of this Attribute. The value is tested for validity and cast to the Attribute's type."""
        filter_result = self.filter(value)
        if filter_result[0]:
            self._value = value if isinstance(value, self.TYPE) else self.TYPE(value) #type: ignore
            if update:
                self._component.model.update_manager.notify_observers(self._component.id, self.ID)
                print(f"detected change in {self._component}, changed attribute: {self.NAME}")
        return filter_result

    def filter(self, value) -> tuple[bool, str]:
        """Verify if a value is valid for this Attribute. If valid, it returns True and an empty string.
        If not valid, it returns False and an explanation."""
        return True, ""

    @property
    def description(self) -> str:
        """Provides a short description about what the value of the Attribute means to display in the UI. 
        By default gives the Attribute's unit."""
        return self.NAME + (f" (in {self.UNIT})" if self.UNIT != "" else "")

    def get_display_value(self) -> str:
        """Return the value of the Attribute in a way that it can be displayed in the UI. By default casts value to string."""
        return str(self.get_value())


class AttributeDescriptor(Generic[V]):
    """Make the value of an Attribute directly accessible from the Component. 
    When the user requests an Attribute, for example Node.id, the value of the Attribute is returned and not the Attribute itself."""

    def __init__(self, attr_name: str):
        """Create an instance of AttributeDescriptor."""
        self.attr_name: str = attr_name

    def __get__(self, instance, owner) -> V:
        return getattr(instance, self.attr_name).get_value()

    def __set__(self, instance, value: V) -> tuple[bool, str]:
        return getattr(instance, self.attr_name).set_value(value)


class Component(ABC):
    """Base class for all Components in the Model."""

    TAG: str = "component"

    id: AttributeDescriptor[str] = AttributeDescriptor("_id")

    def __init__(self, model: 'Model', id: str | None=None):
        """Create an instance of Component."""
        self.model: Model = model
        self.attributes: list[Attribute] = []
        self._id: IdAttribute = IdAttribute(self, id)

    @classmethod
    def dummy(cls):
        """Create a dummy instance of Component to extract its Attributes."""
        return cls(Model(UpdateManager()), id="")

    @abstractmethod
    def delete(self):
        """Deletes the Component from the model and modifies Components dependent on it."""

    @staticmethod
    def gen_id(i: int) -> str:
        """Generate an id based on a number i."""
        return str(i)


class IdAttribute(Attribute[Component, str]):
    """Id Attribute assigned to all Components. Every id is validated to exist only once in the model 
    and thus able to uniquely identify the Component."""

    TYPE = str
    ID = "id"
    NAME = "Id"
    UNIT = ""
    EDITABLE: bool = True

    def __init__(self, component: Component, value: str | None) -> None:
        """Create an instance of IdAttribute."""
        super().__init__(component, value if value else "")
        if not value:
            self._value = self._component.model.next_unique_id_for(type(component))
    
    def filter(self, value) -> tuple[bool, str]:
        """Verify if value already used as an id in the model."""
        if hasattr(self._component, "_id") and self._component.id == value:
            return True, ""
        if value in {component.id for component in self._component.model.all_components}:
            return False, "Id already exists."
        return True, ""


class Node(Component):
    """Node component of the model. Connects Beams. A Node is created automatically at the end of each Beam."""

    TAG: str = "node"

    x: AttributeDescriptor[float] = AttributeDescriptor("_x")
    y: AttributeDescriptor[float] = AttributeDescriptor("_y")

    def __init__(self, model: 'Model', x: float, y: float, id: str | None=None):
        """Create an instance of Node."""
        super().__init__(model, id)
        self._x: XCoordinateAttribute = XCoordinateAttribute(self, x)
        self._y: YCoordinateAttribute = YCoordinateAttribute(self, y)

    @classmethod
    def dummy(cls, x: float=0, y: float=0):
        """Create a dummy instance of Node to extract its Attributes."""
        return cls(Model(UpdateManager()), x, y, id=cls.TAG)

    def delete(self):
        """Delete the Node from the model and delete Supports and Forces at this Node."""
        for support in self.supports: support.delete()
        for force in self.forces: force.delete()
        self.model.nodes.remove(self)

    @property
    def beams(self) -> list['Beam']:
        """Return all Beams in the Model that are connected to this Node."""
        return [beam for beam in self.model.beams if beam.start_node == self or beam.end_node == self]

    @property
    def supports(self) -> list['Support']:
        """Return all Supports on this Node."""
        return [support for support in self.model.supports if support.node == self]

    @property
    def forces(self) -> list['Force']:
        """Return all Forces on this Node."""
        return [force for force in self.model.forces if force.node == self]

    @staticmethod
    def gen_id(i: int) -> str:
        """Return the roman numeral equivalent of i."""
        return int_to_roman(i)


class CoordinateAttribute(Attribute[Node, float]):
    """Base class of coordinate Attributes. Is validated to be a number and rounded when displayed."""

    TYPE = float

    def filter(self, value) -> tuple[bool, str]:
        """Verify that value is a number."""
        try:
            value = float(value)
        except ValueError:
            return False, "Coordinate must be a number."
        return True, ""

    def get_display_value(self) -> str:
        """Return value rounded to 2 decimals."""
        return str(round(self.get_value(), 2))


class XCoordinateAttribute(CoordinateAttribute):
    """X coordinate Attribute used by Nodes."""

    ID = "x"
    NAME = "X"
    UNIT = ""
    EDITABLE: bool = True


class YCoordinateAttribute(CoordinateAttribute):
    """Y coordinate Attribute used by Nodes."""

    ID = "y"
    NAME = "Y"
    UNIT = ""
    EDITABLE: bool = True


class Beam(Component):
    """Beam Component. Connects Nodes in the Model."""

    TAG: str = "beam"

    start_node: AttributeDescriptor[Node] = AttributeDescriptor("_start_node")
    end_node: AttributeDescriptor[Node] = AttributeDescriptor("_end_node")
    length: AttributeDescriptor[float] = AttributeDescriptor("_length")
    angle: AttributeDescriptor[float] = AttributeDescriptor("_angle")

    def __init__(self, model: 'Model', start_node: Node, end_node: Node, id: str | None=None):
        """Create an instance of Beam."""
        super().__init__(model, id)
        self._start_node: StartNodeAttribute = StartNodeAttribute(self, start_node)
        self._end_node: EndNodeAttribute = EndNodeAttribute(self, end_node)
        self._length: BeamLengthAttribute = BeamLengthAttribute(self)
        self._angle: BeamAngleAttribute = BeamAngleAttribute(self)

    @classmethod
    def dummy(cls, start: Node|None=None, end: Node|None=None, id: str|None=None):
        """Create a dummy instance of Beam to extract its Attributes."""
        start = start if start else Node.dummy()
        end = end if end else Node.dummy()
        id = id if id else cls.TAG
        return cls(model=Model(UpdateManager()), start_node=start, end_node=end, id=id)

    def delete(self):
        """Delete Beam from the model and delete adjacent Nodes if they become unconnected."""
        self.model.beams.remove(self)
        if not self.start_node.beams: self.start_node.delete()
        if not self.end_node.beams: self.end_node.delete()

    def calc_length(self) -> float:
        """Calculate and return length of Beam."""
        p1 = Point(self.start_node.x, self.start_node.y)
        p2 = Point(self.end_node.x, self.end_node.y)
        return Line(p1, p2).length_scaled()

    def calc_angle(self) -> float:
        """Calculate and return Beam angle."""
        p1 = Point(self.start_node.x, self.start_node.y)
        p2 = Point(self.end_node.x, self.end_node.y)
        return Line(p1, p2).angle()

    @staticmethod
    def gen_id(i: int) -> str:
        """Return id of form Si."""
        return f"S{i}"


class NodeAttribute(Attribute[Component, Node]):
    """Node Attribute used by Supports and Forces."""

    TYPE = Node
    ID = "node"
    NAME = "Node"
    UNIT = ""
    EDITABLE: bool = False

    def get_display_value(self) -> str:
        """Return id of Node."""
        return self._value.id


class StartNodeAttribute(NodeAttribute):
    """Start Node Attribute used by Beams."""

    ID = "startnode"
    NAME = "Start"
    UNIT = ""
    EDITABLE: bool = False


class EndNodeAttribute(NodeAttribute):
    """End Node Attribute used by Beams."""

    ID = "endnode"
    NAME = "End"
    UNIT = ""
    EDITABLE: bool = False


class BeamAngleAttribute(Attribute[Beam, float]):
    """Beam angle Attribute used by Beams."""

    TYPE = float
    ID = "angle"
    NAME = "Angle"
    UNIT = "°"
    EDITABLE: bool = True

    def __init__(self, component: Beam) -> None:
        """Create an instance of BeamAngleAttribute."""
        super().__init__(component, 0)

    def filter(self, value) -> tuple[bool, str]:
        """Verify that value is a number between 0 and 360."""
        try:
            value = float(value)
        except ValueError:
            return False, "Angle must be a number."
        if not 0 <= value <= 360:
            return False, "Angle must be between 0 and 360."
        return True, ""

    def get_value(self) -> float:
        """Calculate and return angle of Beam."""
        return self._component.calc_angle()

    def get_display_value(self) -> str:
        """Return value rounded to 2 decimals."""
        return str(round(self.get_value(), 2))

    def set_value(self, value, update: bool=True) -> tuple[bool, str]:
        """Set Beam angle value by calculating new position for and moving its end Node."""
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
    """Attribute for Beam length."""

    TYPE = float
    ID = "length"
    NAME = "Length"
    UNIT = "m"
    EDITABLE: bool = True

    def __init__(self, component: Beam) -> None:
        """Create an instance of BeamLengthAttribute."""
        super().__init__(component, 0)

    def filter(self, value) -> tuple[bool, str]:
        """Verify that value is a positive number."""
        try:
            value = float(value)
        except ValueError:
            return False, "Length must be a number."
        if not 0 < value:
            return False, "Length must be positive."
        return True, ""

    def get_value(self) -> float:
        """Calculate and return Beam length."""
        return self._component.calc_length()

    def get_display_value(self) -> str:
        """Return value rounded to 2 decimals."""
        return str(round(self.get_value(), 2))

    def set_value(self, value, update: bool=True) -> tuple[bool, str]:
        """Set Beam length value by calculating and setting new position for it's end Node."""
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
    """Support Component in Model. Can be attached to Beams in any angle and have 1 or 2 DOF."""

    TAG: str = "support"

    node: AttributeDescriptor[Node] = AttributeDescriptor("_node")
    angle: AttributeDescriptor[float] = AttributeDescriptor("_angle")
    constraints: AttributeDescriptor[int] = AttributeDescriptor("_constraints")

    def __init__(self, model: 'Model', node: Node, angle: float=180, constraints: int=2, id: str | None=None):
        """Create an instance of Support."""
        super().__init__(model, id)
        self._node: NodeAttribute = NodeAttribute(self, node)
        self._angle: AngleAttribute = AngleAttribute(self, angle)
        self._constraints: ConstraintsAttribute = ConstraintsAttribute(self, constraints)

    @classmethod
    def dummy(cls):
        """Create a dummy instance of Support to extract its Attributes."""
        return cls(Model(UpdateManager()), Node.dummy(), id="")

    def delete(self):
        """Delete Support from the model."""
        self.model.supports.remove(self)

    @staticmethod
    def gen_id(i: int) -> str:
        """Get capital letter at index i of the alphabet as id."""
        return chr(i + 64)


class AngleAttribute(Attribute[Component, float]):
    """Angle Attribute used by Supports and Forces."""

    TYPE = float
    ID = "angle"
    NAME = "Angle"
    UNIT = "°"
    EDITABLE: bool = True

    def filter(self, value) -> tuple[bool, str]:
        """Verify that value is a number between 0 and 360."""
        try:
            value = float(value)
        except ValueError:
            return False, "Angle must be a number."
        if not 0 <= value <= 360:
            return False, "Angle must be between 0 and 360."
        return True, ""

    def get_display_value(self) -> str:
        """Return value rounded to two decimals."""
        return str(round(self.get_value(), 2))


class ConstraintsAttribute(Attribute[Support, int]):
    """Constraints Attribute used by Supports to specify how many degrees of freedom they allow."""

    TYPE = int
    ID = "constraints"
    NAME = "Constraints"
    UNIT = ""
    EDITABLE: bool = True

    def filter(self, value) -> tuple[bool, str]:
        """Verify that value is 1 or 2."""
        try:
            value = int(value)
        except ValueError:
            return False, "Must be 1 or 2."
        if not value in {1, 2}:
            return False, "Must be 1 or 2."
        return True, ""


class Force(Component):
    """Force Component in Model. Can be attached to a Node at any angle."""

    TAG: str = "force"

    node: AttributeDescriptor[Node] = AttributeDescriptor("_node")
    angle: AttributeDescriptor[float] = AttributeDescriptor("_angle")
    strength: AttributeDescriptor[float] = AttributeDescriptor("_strength")

    def __init__(self, model: 'Model', node: Node, angle: float=0, strength: float=50.0, id: str | None=None):
        """Create an instance of Force."""
        super().__init__(model, id)
        self._node: NodeAttribute = NodeAttribute(self, node)
        self._angle: AngleAttribute = AngleAttribute(self, angle)
        self._strength: StrengthAttribute = StrengthAttribute(self, strength)

    @classmethod
    def dummy(cls, id="", node: Node | None=None, angle: float=0, strength: float=50.0):
        """Create a dummy instance of Force to extract its Attributes."""
        node = Node.dummy() if node == None else node
        dummy_force: Force = cls(Model(UpdateManager()), node, angle, strength, id=id)
        return dummy_force

    def delete(self):
        """Remove Force from the Model."""
        self.model.forces.remove(self)

    @staticmethod
    def gen_id(i: int) -> str:
        """Return id of form Fi."""
        return f"F{i}"


class StrengthAttribute(Attribute[Force, float]):
    """Strength Attribute used by Forces."""

    TYPE = float
    ID = "strength"
    NAME = "Strength"
    UNIT = "kN"
    EDITABLE: bool = True

    def filter(self, value) -> tuple[bool, str]:
        """Verify that value is a number."""
        try:
            value = float(value)
        except ValueError:
            return False, "Strength must be a number."
        return True, ""


class ForceType(Enum):
    """Force type to describe results from solving the Model. 
    Can be either 0 if Force strength is 0, COMPRESSIVE if Force strength is < 0
    or TENSILE if Force is > 0."""

    COMPRESSIVE = "C"
    ZERO = "0"
    TENSILE = "T"

    @classmethod
    def from_value(cls, value: float):
        """Get Force type for a strength value. Can be either 0 if Force strength is 0, 
        COMPRESSIVE if strength is < 0 or TENSILE if strength is > 0."""
        if value < 0:
            return cls.COMPRESSIVE
        elif value == 0:
            return cls.ZERO
        else:
            return cls.TENSILE


class Result(Component):
    """Result Component used to describe the solution forces from solving the Model."""

    TAG: str = "result"

    force_type: AttributeDescriptor[ForceType] = AttributeDescriptor("_force_type")
    result: AttributeDescriptor[float] = AttributeDescriptor("_result")

    def __init__(self, model: 'Model', force: Force, id: str | None=None):
        """Create an instance of Result."""
        super().__init__(model, id)
        self._id._value = force.id
        self._force_type: ForceTypeAttribute = ForceTypeAttribute(self, ForceType.from_value(round(force.strength, 2)))
        self._result: ResultAttribute = ResultAttribute(self, round(force.strength, 2))

    @classmethod
    def dummy(cls, force: Force | None=None, id=""):
        """Create a dummy instance of Result to extract its Attributes."""
        force = force if force else Force.dummy()
        dummy_result: Result = cls(Model(UpdateManager()), force)
        dummy_result._id._value = id
        return dummy_result

    def delete(self):
        """Doesn't to anything. Implemented because method is declared as abstract in base class."""
        pass


class ResultAttribute(Attribute[Result, float]):
    """Result attribute used for Result Component to describe its strength. 
    Can not be edited by the user unlike StrengthAttribute used by Force."""

    TYPE = float
    ID = "result"
    NAME = "Strength"
    UNIT = "kN"
    EDITABLE: bool = False

    def filter(self, value) -> tuple[bool, str]:
        """Verify that value is a number."""
        try:
            value = float(value)
        except ValueError:
            return False, "Result must be a number."
        return True, ""

    def get_display_value(self) -> str:
        """Return value cast to string. If 0 add 0 decimal for better appearance in UI."""
        return str(0.0 if self.get_value() == 0 else self.get_value())


class ForceTypeAttribute(Attribute[Result, ForceType]):
    """Force type Attribute. Is expressed as ForceType enum value. Used by Result Components."""

    TYPE = ForceType
    ID = "force_type"
    NAME = "Type"
    UNIT = ""
    EDITABLE: bool = False

    def get_display_value(self) -> str:
        """Return abbreviated representation of ForceType.
        0 for 0, C for compressive, T for tensile"""
        return self.get_value().value


class Model:
    def __init__(self, update_manager: UpdateManager):
        """Create an instance of Model."""
        self.nodes: ComponentList[Node] = ComponentList(Node, update_manager)
        self.beams: ComponentList[Beam] = ComponentList(Beam, update_manager)
        self.supports: ComponentList[Support] = ComponentList(Support, update_manager)
        self.forces: ComponentList[Force] = ComponentList(Force, update_manager)

        self.update_manager: UpdateManager = update_manager

    def clear(self):
        """Remove all components from the Model. Notify Model Observers of change."""
        if not self.is_empty():
            [component_list.clear() for component_list in self.component_lists]
        self.update_manager.notify_observers()

    def is_empty(self) -> bool:
        """Returns True if the Model is empty, eg. doesn't contain any Components."""
        return all(not component_list for component_list in self.component_lists)

    @property
    def component_lists(self):
        """Returns all ComponentLists in the Model as a tuple for iteration."""
        return (self.nodes, self.beams, self.supports, self.forces)

    @property
    def all_components(self) -> list[Component]:
        """Returns all Components of all types in the Model."""
        return [component for component_list in self.component_lists for component in component_list]

    def list_for_type(self, component_type: Type[C]) -> 'ComponentList[C]':
        """Returns the Models ComponentList for the specified type if it exists."""
        return cast('ComponentList[C]', next(component_list for component_list in self.component_lists if component_list.component_class == component_type))

    def next_unique_id_for(self, component_type: type[C]) -> str:
        """Generate the next unique id that is not already present in the Model for a Component type."""
        existing_ids =  {component.id for component in self.all_components}
        i = 1
        while component_type.gen_id(i) in existing_ids:
            i += 1
        return component_type.gen_id(i)

    def is_valid(self) -> bool:
        """Returns True if the Model is valid, eg. ready for solving."""
        return all([
            not self.is_empty(),
            len(self.forces) > 0,
            self.has_three_reaction_forces(),
            self.is_connected(),
            self.is_stat_det(),
            self.is_stable(),
            not self.has_overlapping_beams()
        ])

    def is_stat_det(self) -> bool:
        """Check if the model is statically determined and thus ready for analysis. Used for Model validation."""
        return ((2 * len(self.nodes)) - (sum(support.constraints for support in self.supports) + len(self.beams))) == 0

    def is_stable(self) -> bool:
        """Returns True if the Model is stable. Used for Model validation."""
        return self.is_empty() or not any([
            sum(support.constraints for support in self.supports) < 3,
            self.supports_parallel(),
            self.all_supports_intersect(),
            not self.is_connected(),
            self.has_non_triangular_shapes()])

    def is_connected(self) -> bool:
        """Returns True if the graph of the Model is connected. Meaning all Components in the Model are connected to each other.
        Uses DFS (depth-first-search) to traverse all Beams of the Model from a random start point. If the number of Nodes found is
        equal to the total number of Nodes in the System, the Model is connected. Used for Model validation."""
        if self.is_empty():
            return True
        else:
            adj: dict[Node, list[Node]] = {}
            for node in self.nodes:
                adj[node] = []
            for beam in self.beams:
                adj[beam.start_node].append(beam.end_node)
                adj[beam.end_node].append(beam.start_node)
            visited: list[Node] = []
            def dfs(node: Node, visited: list[Node]):
                visited.append(node)
                [dfs(neighbor, visited) for neighbor in adj[node] if neighbor not in visited]
            dfs(self.nodes[0], visited)
            return len(visited) == len(self.nodes)

    def has_three_reaction_forces(self) -> bool:
        """Returns True if the Model has exactly three reaction forces. 
        Calculated by counting the number of constraints for all Supports in the Model. Used for Model validation."""
        return sum(support.constraints for support in self.supports) == 3

    def has_overlapping_beams(self) -> bool:
        """Returns False if the Model has Beams that are intersecting each other. Used for Model validation."""
        beam_to_line: Callable[[Beam], Line] = lambda beam: Line(Point(beam.start_node.x, beam.start_node.y), Point(beam.end_node.x, beam.end_node.y))
        return any(beam_to_line(b1).intersects(beam_to_line(b2)) for b1, b2 in itertools.combinations(self.beams, 2))

    def has_non_triangular_shapes(self):
        """Returns True if the Model contains non triangular Shapes. Every Beam in the Model should be connected in a way that it
        forms a triangle with two other Beams. Used for Model validation.\n
        The algorithm saves a list of connected Beams sorted by their angle relative to the Node for every Node in the Model. 
        So for each Beam two copies are made (one for each direction).
        Then starting from a random Node the algorithm walks in counterclockwise direction in the tightest possible circle until it reaches back to the start Node.
        This is repeated until there are no Beams unvisited in the Model. The steps it takes for each circle are stored and verified to be no bigger than 3,
        except for one circle that goes around the outside of the Model."""
        if self.is_empty() or self.has_overlapping_beams() or not self.is_connected():
            return False
        if any(len(node.beams) < 2 for node in self.nodes):
            return True
        beams_for_nodes: Callable[[Node], list[Beam]] = lambda node: [Beam.dummy(node, beam.start_node if not beam.start_node == node else beam.end_node, beam.id) for beam in node.beams]
        sorted_beams = {node: sorted(beams_for_nodes(node), key=lambda beam: self.rel_beam_angle(node, beam)) for node in self.nodes}
        orders: list[int] = []
        next_beam = sorted_beams[self.nodes[0]][0]
        while(next_beam):
            orders.append(self.find_face(sorted_beams, next_beam.start_node, next_beam, 0))
            next_beam = next((beam for beams in sorted_beams.values() for beam in beams), None)
        return len([order for order in orders if order > 3]) > 1

    def find_face(self, sorted_beams: dict[Node, list[Beam]], start_node: Node, beam: Beam, count: int):
        """Find a face, eg. a circle of Beams in the Model. Used by method has_non_triangular_shapes to verify triangularity."""
        sorted_beams[beam.start_node].remove(beam)
        count += 1
        if beam.end_node == start_node:
            return count
        else:
            incoming_angle = self.rel_beam_angle(beam.end_node, beam)
            smaller_angle_beams = [beam for beam in  sorted_beams[beam.end_node] if beam.angle < incoming_angle]
            next_beam = smaller_angle_beams[-1] if smaller_angle_beams else sorted_beams[beam.end_node][-1]
            return self.find_face(sorted_beams, start_node, next_beam, count)

    def rel_beam_angle(self, node: Node, beam: Beam) -> float:
        """Return the Beam angle relative to (with the Beam starting from) the Node."""
        start, end = (beam.start_node, beam.end_node) if beam.start_node == node else (beam.end_node, beam.start_node)
        return Line(Point(start.x, start.y), Point(end.x, end.y)).angle()

    def supports_parallel(self):
        """Check if all Supports in the Model have a parallel line of action. Used for Model validation."""
        if len(self.supports) > 2 and all(support.constraints == 1 for support in self.supports):
            return all(self.supports[0].angle % 180 == support.angle % 180 for support in self.supports)
        return False

    def all_supports_intersect(self):
        """Check if all lines of action of Supports in the Model intersect in a single point. Used for Model validation."""
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
        """Check if two lines of action of Supports in the Model intersect in a single point. Used for Model validation."""
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
            """Get the line equation of form "y = mx + c" of a line of action for a Support."""
            m = -math.tan(math.radians(support.angle))
            c = -(-support.node.y + m * support.node.x)
            return m, c


class ComponentList(list[C]):
    """Component list that holds Components of a single type. When something is added to or removed from the list the Models
    UpdateManager is notified."""

    def __init__(self, component_class: Type[C], update_manager: UpdateManager, *args, **kwargs):
        """Create an instance of ComponentList."""
        super().__init__(*args, **kwargs)
        self.component_class: Type[C] = component_class #Class of the entries in this list, to make it accessible even when the list is empty
        self.update_manager: UpdateManager = update_manager

    def append(self, *components: C) -> None:
        """Add item to the list and notify UpdateManager to update."""
        for component in components: super().append(component)
        self.update_manager.notify_observers()

    def remove(self, *components: C) -> None:
        """Remove item(s) from the list and notify UpdateManager to update."""
        [super().remove(component) for component in components if component in self]
        self.update_manager.notify_observers()

    def component_for_id(self, id: str) -> C | None:
        """Get a component from the list by searching for its"""
        return next((component for component in self if component.id == id), None)