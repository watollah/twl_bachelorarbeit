import math
from c2d_app import TwlApp
from c2d_math import Point, Line, Polygon
from c2d_components import Component, Node, Beam, Support, Force


class CremonaAlgorithm:
    """Takes the result Forces from Solver class and translates them to the steps needed to draw the corresponding Cremona diagram."""

    FORCE_REF_DISTANCE = 10

    @staticmethod
    def get_steps() -> list[tuple[Node | None, Force, Component, bool]]:
        """Returns the list of steps for the Cremona diagram. Each step contains the following information:
        \nNode: Which Node is the current step happening on, None for initial drawing of outside and reaction Forces.
        \nForce: The Force that is drawn in the current step. Is created as a dummy Force. Takes it's id from the Component that it belongs to.
        \nComponent: The Component that the current step's Force originates from. Beam for beam forces, Support for reaction forces, Force for outside forces
        \nbool: Is the current step a sketching step? (The dashed lines in the Cremona Diagram)"""
        support_forces = {force: component for force, component in TwlApp.solver().solution.items() if isinstance(component, Support)}
        beam_forces = {force: component for force, component in TwlApp.solver().solution.items() if isinstance(component, Beam)}
        forces_for_nodes = {node: CremonaAlgorithm._get_forces_for_node(node, support_forces, beam_forces) for node in TwlApp.model().nodes}

        steps: list[tuple[Node | None, Force, Component, bool]] = [(None, force, force, False) for force in TwlApp.model().forces]
        steps.extend([(None, force, support, False) for force, support in support_forces.items()])
        CremonaAlgorithm._sort_outside_forces(steps)
        node = CremonaAlgorithm._find_next_node(forces_for_nodes, steps)
        while node:
            start_angle = CremonaAlgorithm._get_start_angle(forces_for_nodes[node], steps)
            sorted_forces = dict(sorted(forces_for_nodes[node].items(), key=lambda item: (item[0].angle - start_angle) % 360))
            to_be_added = []
            for force, component in sorted_forces.items():
                if any(step[1].id == force.id for step in steps):
                    steps.extend(to_be_added)
                    to_be_added.clear()
                    steps.append((node, force, component, False))
                else:
                    steps.append((node, force, component, True))
                    to_be_added.append((node, force, component, False))
            steps.extend(to_be_added)
            forces_for_nodes.pop(node)
            node = CremonaAlgorithm._find_next_node(forces_for_nodes, steps)
        return steps

    @staticmethod
    def _sort_outside_forces(steps: list[tuple[Node | None, Force, Component, bool]]):
        """Sort the Force Components and reaction forces by clockwise order around the Model.
        Finds the midpoint of all outside forces and draws a line from this point to each force.
        Then sorts all the forces using the angles of these lines."""
        points = {force: CremonaAlgorithm._ref_point_for_force(force) for node, force, component, sketch in steps}
        midpoint = Polygon(*points.values()).midpoint()
        angles = {force: Line(midpoint, points[force]).angle() for force in points.keys()}
        start_angle = angles[TwlApp.model().forces[0]]
        steps.sort(key=lambda step: (angles[step[1]] - start_angle) % 360)

    @staticmethod
    def _ref_point_for_force(force: Force) -> Point:
        """Determine the position reference point for each Force. The position of the Force has to be offset slightly from it's Node 
        in the direction that it's coming from. If the Forces use the Node itself as a reference point, then the clockwise ordering of
        outside Forces around the Model would not be possible."""
        start = Point(force.node.x, force.node.y)
        end = Point(force.node.x, force.node.y - CremonaAlgorithm.FORCE_REF_DISTANCE)
        line = Line(start, end)
        line.rotate(start, force.angle)
        return line.end

    @staticmethod
    def _get_forces_for_node(node: Node, support_forces: dict[Force, Support], beam_forces: dict[Force, Beam]) -> dict[Force, Component]:
        """Get all forces for a Node (Forces, Beam forces and reaction forces)"""
        forces: dict[Force, Component] = {force: force for force in node.forces}
        forces.update({force: support for force, support in support_forces.items() if force.node == node})
        forces.update(CremonaAlgorithm._get_beam_forces_on_node(node, beam_forces))
        return forces

    @staticmethod
    def _get_beam_forces_on_node(node: Node, beam_forces: dict[Force, Beam]) -> dict[Force, Beam]:
        """Get all Beam forces for a Node. The angle is calculated as the Beam angle relative to the Node."""
        forces: dict[Force, Beam] = {}
        for beam in node.beams:
            other_node = beam.start_node if beam.start_node != node else beam.end_node
            angle = Line(Point(node.x, node.y), Point(other_node.x, other_node.y)).angle()
            strength = next((force.strength for force in beam_forces.keys() if force.id == beam.id))
            forces[Force.dummy(beam.id, node, angle, strength)] = beam
        return forces

    @staticmethod
    def _find_next_node(forces_for_nodes: dict[Node, dict[Force, Component]], steps: list[tuple[Node | None, Force, Component, bool]]):
        """Find next Node to traverse for Cremona algorithm. Has to have max 2 unknown forces and min 1 known force."""
        return next((node for node in forces_for_nodes.keys() if (CremonaAlgorithm._count_unknown_on_node(list(forces_for_nodes[node].keys()), steps) <= 2) 
                     and (CremonaAlgorithm._count_known_on_node(list(forces_for_nodes[node].keys()), steps) > 0)), None)

    @staticmethod
    def _count_occurences(force: Force, steps: list[tuple[Node | None, Force, Component, bool]]):
        """Count how many times the Force has already been drawn in the Cremona diagram."""
        return [step[1].id for step in steps].count(force.id)

    @staticmethod
    def _count_unknown_on_node(forces_for_node: list[Force], steps: list[tuple[Node | None, Force, Component, bool]]) -> int:
        """Count how many unknown Forces there are left at the Node."""
        return sum(CremonaAlgorithm._count_occurences(force, steps) == 0 for force in forces_for_node)

    @staticmethod
    def _count_known_on_node(forces_for_node: list[Force], steps: list[tuple[Node | None, Force, Component, bool]]) -> int:
        """Count how many known Forces there are left at the Node."""
        return sum(CremonaAlgorithm._count_occurences(force, steps) > 0 for force in forces_for_node)

    @staticmethod
    def _get_start_angle(forces: dict[Force, Component], steps: list[tuple[Node | None, Force, Component, bool]]):
        """Find the angle of the Force that should be drawn first in the diagram for the current Node. Has to be already drawn at least once."""
        return next((force.angle for force in forces.keys() if CremonaAlgorithm._count_occurences(force, steps) > 0 and not math.isclose(force.strength, 0)), 0)