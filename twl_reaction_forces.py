import numpy as np

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
        node_for_moments = next(support.node for support in self.statical_system.supports if support.constraints == 2)
        hor_forces = [self.get_axial_force_component(force, Orientation.HORIZONTAL) for force in self.statical_system.forces]
        vert_forces = [self.get_axial_force_component(force, Orientation.VERTICAL) for force in self.statical_system.forces]
        moment_force_factors = self.calculate_force_moment_factors(self.statical_system.forces, node_for_moments)
        moments = [(force.strength * factor) for force, factor in zip(self.statical_system.forces, moment_force_factors)]
        result_vector = [-sum([force.strength for force in hor_forces]), -sum([force.strength for force in vert_forces]), -sum(moments)]

        unknowns = self.get_unknown_forces()
        hor_unknowns_factors = self.get_unknown_force_factors(unknowns, Orientation.HORIZONTAL)
        vert_unknowns_factors = self.get_unknown_force_factors(unknowns, Orientation.VERTICAL)
        moment_unknowns_factors = self.calculate_force_moment_factors(unknowns, node_for_moments)
        factors = [hor_unknowns_factors, vert_unknowns_factors, moment_unknowns_factors]

        solved = np.linalg.solve(factors, result_vector).tolist()

        print("Horizontal known forces: " + ", ".join([f"{force.id}={self.format_float(force.strength)}" for force in hor_forces]))
        print("Vertical known forces: " + ", ".join([f"{force.id}={self.format_float(force.strength)}" for force in vert_forces]))
        print(f"Result (node for moments = {node_for_moments.id}):")
        self.print_result(factors , unknowns, result_vector, solved)

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

    def calculate_force_moment_factors(self, forces: List[Force], node: Node) -> List[float]:
        factors: List[float] = []
        node_point = Point(node.x, node.y)
        for force in forces:
            force_node_point = Point(force.node.x, force.node.y)
            force_line = Line(force_node_point, Point(force_node_point.x, force_node_point.y - 10000))
            force_line.rotate(force_node_point, force.angle)
            distance = node_point.distance_to_line(force_line)
            factor = self.direction_to_factor.get(force_line.direction_to_point(node_point), 0)
            factors.append(factor * distance)
        return factors

    def print_result(self, factors: List[List[float]], unknown_forces: List[Force], result: List[float], solved: List[float]):
        unknown_force_str = [force.id for force in unknown_forces]
        factors_max_width = max(len(self.format_float(f)) for row in factors for f in row)
        factors_total_width = factors_max_width * len(unknown_forces) + len(unknown_forces) - 1 + 2
        unknowns_max_width = max(len(force) for force in unknown_force_str)
        result_max_width = max(len(self.format_float(f)) for f in result)
        solved_max_width = max(len(self.format_float(f)) for f in solved)
        center_index = len(unknown_forces) // 2
        for i, force in enumerate(unknown_forces):
            factors_matrix = factors_total_width * " "
            y = i - center_index + 1
            if 0 <= y <= 2:
                factors_matrix = self.matrix_row(factors, y)
            space1 = "   " if i != center_index else " x "
            space2 = "   " if i != center_index else " = "
            space3 = "    " if i != center_index else " -> "
            print(factors_matrix + space1 + f"[{unknown_force_str[i].ljust(unknowns_max_width)}]" 
                  + space2 + f"[{self.format_float(result[i]).ljust(result_max_width)}]" 
                  + space3 + f"[{self.format_float(solved[i]).ljust(solved_max_width)}]")

    def matrix_row(self, factors: List[List[float]], i: int):
        factors_max_width = max(len(self.format_float(factor)) for row in factors for factor in row)
        return "[{}]".format(" ".join(self.format_float(factor).ljust(factors_max_width) for factor in factors[i]))

    def print_vector(self, vector: List[float]):
        max_width = max(len(self.format_float(value)) for value in vector)
        for value in vector:
            print(f"[{self.format_float(value).ljust(max_width)}]")

    def format_float(self, f) -> str:
        return "{:.2f}".format(f)