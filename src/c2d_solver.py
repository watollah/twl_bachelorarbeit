import numpy as np
import math

from c2d_math import Orientation, Point, Line
from c2d_components import Model, Component, Node, Beam, Force


class Solver:
    """Converts the Model into a system of linear equations and uses numpy to solve those equations."""

    def __init__(self, model: Model) -> None:
        """Create an instance of Solver."""
        self.model = model

        self.factor_matrix: list[list[float]] = []
        self.result_vector: list[float] = []
        self.solution: dict[Force, Component] = {}

    def solve(self):
        """Solve the model by constructing the system of linear equations and solving them with np.linalg.solve."""
        self.reset()
        if not self.model.is_valid():
            return

        self.solution = self.get_unknown_forces()

        for node in self.model.nodes:
            self.factor_matrix.append(self.get_node_factors(node, Orientation.HORIZONTAL))
            self.factor_matrix.append(self.get_node_factors(node, Orientation.VERTICAL))
            self.result_vector.append(self.get_node_forces(node, Orientation.HORIZONTAL))
            self.result_vector.append(self.get_node_forces(node, Orientation.VERTICAL))

        np_solution = np.linalg.solve(self.factor_matrix, self.result_vector).tolist()
        for i, force in enumerate(self.solution.keys()):
            force._strength._value = np_solution[i]
        self.print_result()

    def reset(self):
        """Reset the solver by deleting the equation and solution."""
        self.factor_matrix = []
        self.result_vector = []
        self.solution = {}

    def get_unknown_forces(self) -> dict[Force, Component]:
        """Returns a list of all the unknown forces in the system mapped to the component that they belong to. 
        Includes reaction forces and beam forces."""
        unknown_forces: dict[Force, Component] = {}
        for support in self.model.supports:
            if support.constraints == 2:
                unknown_forces[Force.dummy(f"{support.id}_h", support.node, 270)] = support
                unknown_forces[Force.dummy(f"{support.id}_v", support.node, 180)] = support
            if support.constraints == 1:
                unknown_forces[Force.dummy(support.id, support.node, support.angle)] = support
        for beam in self.model.beams:
            unknown_forces[Force.dummy(beam.id, angle=beam.angle)] = beam
        return unknown_forces

    def get_node_factors(self, node: Node, orientation: Orientation) -> list[float]:
        """Get all the factors for one Node and orientation for a row of the factor matrix A in Ax = b.
        Specifies for all unknown forces in the Model the extend to which these forces are present on the Node in the specified orientation/direction."""
        factors: list[float] = []
        for support in self.model.supports:
            support_factors = self.generate_factors((support.angle + 180) % 360)
            factors.extend(support_factors[(support in node.supports, support.constraints, orientation)])
        for beam in self.model.beams:
            beam_factors = self.generate_factors(self.beam_angle(node, beam))
            factors.extend(beam_factors[(beam in node.beams, 1, orientation)])
        return factors

    def get_node_forces(self, node: Node, orientation: Orientation) -> float:
        """Get the sum of the strength of all Force components in the Model on this Node in the specified orientation.
        This is used for the entry for the Node in the result vector b of Ax = b."""
        forces: list[float] = []
        for force in self.model.forces:
            force_factors = self.generate_factors((force.angle + 180) % 360)
            forces.append(force_factors[(force in node.forces, 1, orientation)][0] * force.strength)
        return -sum(forces)

    def generate_factors(self, angle: float) -> dict[tuple[bool, int, Orientation], list[float]]:
        """Get a mapping for a factor for an unknown force on a Node depending on if the force exists on the Node, how many constraints it has 
        (only relevant if it's a Support), and in which orientation I'm interested. If it doesn't exist or doesn't go at all in the specified direction
        then the factor is 0. If it exists and goes completely in the specified direction the factor is 1. If it goes in part in the specified direction then
        the factor is determined using sin/cos."""
        return {
            #(exists on node, no of constraints, orientation): factors
            (True, 1, Orientation.HORIZONTAL): [math.sin(math.radians(angle))],
            (True, 1, Orientation.VERTICAL): [math.cos(math.radians(angle))],
            (True, 2, Orientation.HORIZONTAL): [1, 0],
            (True, 2, Orientation.VERTICAL): [0, 1],
            (False, 1, Orientation.HORIZONTAL): [0],
            (False, 1, Orientation.VERTICAL): [0],
            (False, 2, Orientation.HORIZONTAL): [0, 0],
            (False, 2, Orientation.VERTICAL): [0, 0]
        }

    def beam_angle(self, node: Node, beam: Beam) -> float:
        """Get the angle of a beam relative to the specified Node (using the Node as the start Node)."""
        if beam in node.beams:
            other_node = beam.start_node if beam.start_node != node else beam.end_node
            return Line(Point(node.x, node.y), Point(other_node.x, other_node.y)).angle()
        return beam.angle

    def print_result(self):
        """Used for debug-purposes to print a readable representation of the matrix equation and the solution vector in the console."""
        unknown_forces = list(self.solution.keys())

        prefix_max_width = max(len(node.id) for node in self.model.nodes) + 8
        factors_max_width = max(len(self.format_float(f)) for row in self.factor_matrix for f in row)
        unknowns_max_width = max(len(force.id) for force in unknown_forces)
        result_max_width = max(len(self.format_float(f)) for f in self.result_vector)
        solved_max_width = max(len(self.format_float(force.strength)) for force in unknown_forces)

        center_index = len(unknown_forces) // 2
        for i in range(len(unknown_forces)):
            orientation = Orientation.HORIZONTAL if i % 2 == 0 else Orientation.VERTICAL
            prefix = f"({self.model.nodes[i // 2].id}, {orientation.value}) ".ljust(prefix_max_width)
            space1 = "   " if i != center_index else " x "
            space2 = "   " if i != center_index else " = "
            space3 = "    " if i != center_index else " -> "
            print(prefix + "[{}]".format(" ".join(self.format_float(factor).ljust(factors_max_width) for factor in self.factor_matrix[i])) 
                  + space1 + f"[{unknown_forces[i].id.ljust(unknowns_max_width)}]" 
                  + space2 + f"[{self.format_float(self.result_vector[i]).ljust(result_max_width)}]" 
                  + space3 + f"[{self.format_float(unknown_forces[i].strength).ljust(solved_max_width)}]")

    def format_float(self, f) -> str:
        """Format a float value to display it neatly in the console."""
        return "{:.2f}".format(f)