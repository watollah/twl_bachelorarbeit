from twl_app import TwlApp
from twl_math import Point, Line, Polygon
from twl_components import Component, Node, Beam, Support, Force


class CremonaAlgorithm:

    @staticmethod
    def get_steps() -> list[tuple[Node | None, Force, Component]]:
        support_forces = {force: component for force, component in TwlApp.solver().solution.items() if isinstance(component, Support)}
        beam_forces = {force: component for force, component in TwlApp.solver().solution.items() if isinstance(component, Beam)}
        forces_for_nodes = {node: CremonaAlgorithm._get_forces_for_node(node, support_forces, beam_forces) for node in TwlApp.model().nodes}

        steps: list[tuple[Node | None, Force, Component]] = [(None, force, force) for force in TwlApp.model().forces]
        steps.extend([(None, force, support) for force, support in support_forces.items()])
        CremonaAlgorithm._sort_outside_forces(steps)
        node = CremonaAlgorithm._find_next_node(forces_for_nodes, steps)
        while node:
            start_angle = CremonaAlgorithm._get_start_angle(forces_for_nodes[node], steps)
            sorted_forces = dict(sorted(forces_for_nodes[node].items(), key=lambda item: (item[0].angle - start_angle) % 360))
            steps.extend([(node, force, component) for force, component in sorted_forces.items()])
            forces_for_nodes.pop(node)
            node = CremonaAlgorithm._find_next_node(forces_for_nodes, steps)
        for i, step in enumerate(steps):
            node = step[0].id if step[0] else "None"
            print(f"Step {i}: {node}, {step[1].id}, {step[2].id}")
        return steps

    @staticmethod
    def _sort_outside_forces(steps: list[tuple[Node | None, Force, Component]]):
        points = {force: Point(force.node.x, force.node.y) for node, force, component in steps}
        midpoint = Polygon(*points.values()).midpoint()
        angles = {force: Line(midpoint, points[force]).angle() for force in points.keys()}
        start_angle = angles[TwlApp.model().forces[0]]
        steps.sort(key=lambda step: (angles[step[1]] - start_angle) % 360)

    @staticmethod
    def _get_forces_for_node(node: Node, support_forces: dict[Force, Support], beam_forces: dict[Force, Beam]) -> dict[Force, Component]:
        forces: dict[Force, Component] = {force: force for force in node.forces}
        forces.update({force: support for force, support in support_forces.items() if force.node == node})
        forces.update(CremonaAlgorithm._get_beam_forces_on_node(node, beam_forces))
        return forces

    @staticmethod
    def _get_beam_forces_on_node(node: Node, beam_forces: dict[Force, Beam]) -> dict[Force, Beam]:
        forces: dict[Force, Beam] = {}
        for beam in node.beams:
            other_node = beam.start_node if beam.start_node != node else beam.end_node
            angle = Line(Point(node.x, node.y), Point(other_node.x, other_node.y)).angle()
            strength = next((force.strength for force in beam_forces.keys() if force.id == beam.id))
            forces[Force.dummy(beam.id, node, angle, strength)] = beam
        return forces

    @staticmethod
    def _find_next_node(forces_for_nodes: dict[Node, dict[Force, Component]], steps: list[tuple[Node | None, Force, Component]]):
        return next((node for node in forces_for_nodes.keys() if CremonaAlgorithm._count_unknown_on_node(node, list(forces_for_nodes[node].keys()), steps) <= 2), None)

    @staticmethod
    def _count_occurences(force: Force, steps: list[tuple[Node | None, Force, Component]]):
        return [step[1].id for step in steps].count(force.id)

    @staticmethod
    def _count_unknown_on_node(node: Node, forces_for_node: list[Force], steps: list[tuple[Node | None, Force, Component]]) -> int:
        return sum(CremonaAlgorithm._count_occurences(force, steps) == 0 for force in forces_for_node)

    @staticmethod
    def _get_start_angle(forces: dict[Force, Component], steps: list[tuple[Node | None, Force, Component]]):
        return next((force.angle for force in forces.keys() if CremonaAlgorithm._count_occurences(force, steps) > 0 and force.strength > 0.001), 0)