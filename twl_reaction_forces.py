from twl_components import *

class TwlReactionForcesCalculator:

    direction_to_factor = {
        Direction.CLOCKWISE: -1,
        Direction.COUNTER_CLOCKWISE: 1,
        Direction.COLINEAR: 0
    }

    def __init__(self, statical_system: StaticalSystem) -> None:
        self.statical_system = statical_system
        if statical_system.statically_determined():
            self.calculate_reaction_forces()

    def calculate_reaction_forces(self):
        hor_known_forces = [self.get_axial_force_component(force, Orientation.HORIZONTAL) for force in self.statical_system.forces]
        vert_known_forces = [self.get_axial_force_component(force, Orientation.VERTICAL) for force in self.statical_system.forces]
        unknown_forces = self.get_unknown_forces()
        hor_force_factors = self.get_unknown_force_factors(unknown_forces, Orientation.HORIZONTAL)
        vert_force_factors = self.get_unknown_force_factors(unknown_forces, Orientation.VERTICAL)
        node_for_moments = next(support.node for support in self.statical_system.supports if support.constraints == 2)
        moment_force_factors = self.calculate_unknown_force_moment_factors(unknown_forces, node_for_moments)

        print("Horizontal known forces: " + ", ".join([f"{force.id}={force.strength}" for force in hor_known_forces]))
        print("Vertical known forces: " + ", ".join([f"{force.id}={force.strength}" for force in vert_known_forces]))
        print("Unknown forces: " + ", ".join([force.id for force in unknown_forces]))
        print(f"Factors (node for moments = {node_for_moments.id}):")
        self.print_matrix(hor_force_factors, vert_force_factors, moment_force_factors)

    def get_axial_force_component(self, force: Force, orientation: Orientation) -> Force:
        angle_radians = math.radians(force.angle)
        strength_factor = math.sin(angle_radians) if orientation == Orientation.HORIZONTAL else math.cos(angle_radians)
        axial_force = Force.dummy(f"{force.id}_{orientation.value}", force.node, force.angle, force.strength * strength_factor)
        return axial_force

    def get_unknown_forces(self) -> List[Force]:
        unknown_forces: List[Force] = []
        for support in self.statical_system.supports:
            if support.constraints == 2:
                unknown_forces.append(Force.dummy(f"{support.id}_h", support.node, 90))
                unknown_forces.append(Force.dummy(f"{support.id}_v", support.node, 0))
            if support.constraints == 1:
                angle = (support.angle + 180) % 360
                unknown_forces.append(Force.dummy(support.id, support.node, angle))
        return unknown_forces

    def get_unknown_force_factors(self, unknown_forces: List[Force], orientation: Orientation) -> List[float]:
        factors: List[float] = []
        for force in unknown_forces:
            if orientation == Orientation.HORIZONTAL:
                if force.angle == 90:
                    factors.append(1)
                elif force.angle == 0:
                    factors.append(0)
                else:
                    factors.append(math.sin(math.radians(force.angle)))
            if orientation == Orientation.VERTICAL:
                if force.angle == 90:
                    factors.append(0)
                elif force.angle == 0:
                    factors.append(1)
                else:
                    factors.append(math.cos(math.radians(force.angle)))
        return factors

    def calculate_unknown_force_moment_factors(self, unknown_forces: List[Force], node: Node) -> List[float]:
        factors: List[float] = []
        node_point = Point(node.x, node.y)
        for force in unknown_forces:
            force_node_point = Point(force.node.x, force.node.y)
            force_line = Line(force_node_point, Point(force_node_point.x, force_node_point.y - 1))
            force_line.rotate(force_node_point, force.angle)
            distance = node_point.distance_to_line(force_line)
            factor = self.direction_to_factor.get(force_line.direction_to_point(node_point), 0)
            factors.append(factor * distance)
        return factors

    def print_matrix(self, *rows: List[float]):
        max_width = max(len(self.format_float(f)) for row in rows for f in row)
        for row in rows:
            print("[{}]".format(" ".join(self.format_float(f).ljust(max_width) for f in row)))

    def format_float(self, f) -> str:
        return "{:.2f}".format(f)
