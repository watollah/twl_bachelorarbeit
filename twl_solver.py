import numpy as np
from typing import Tuple, List, Dict

from twl_components import *


class TwlSolver:

    def __init__(self, model: Model) -> None:
        self.model = model

        self.unknown_forces: List[Force] = []
        self.factor_matrix: List[List[float]] = []
        self.result_vector: List[float] = []
        self.solution_vector: List[float] = []

    def solve(self):
        if not self.model.statically_determined() or self.model.is_empty():
            return
        self.unknown_forces = self.get_unknown_forces()
        self.factor_matrix = []
        self.result_vector = []
        for node in self.model.nodes:
            self.factor_matrix.append(self.get_node_factors(node, Orientation.HORIZONTAL))
            self.factor_matrix.append(self.get_node_factors(node, Orientation.VERTICAL))
            self.result_vector.append(self.get_node_forces(node, Orientation.HORIZONTAL))
            self.result_vector.append(self.get_node_forces(node, Orientation.VERTICAL))
        self.solution_vector = np.linalg.solve(self.factor_matrix, self.result_vector).tolist()
        self.print_result()
        self.model.update_manager.update_results()

    def get_unknown_forces(self) -> List[Force]:
        unknown_forces: List[Force] = []
        for support in self.model.supports:
            if support.constraints == 2:
                unknown_forces.append(Force.dummy(f"{support.id}_h", support.node, 90))
                unknown_forces.append(Force.dummy(f"{support.id}_v", support.node, 0))
            if support.constraints == 1:
                angle = (support.angle + 180) % 360
                unknown_forces.append(Force.dummy(support.id, support.node, angle))
        for beam in self.model.beams:
            unknown_forces.append(Force.dummy(beam.id))
        return unknown_forces

    def get_node_factors(self, node: Node, orientation: Orientation) -> List[float]:
        factors: List[float] = []
        for support in self.model.supports:
            support_factors = self.generate_factors((support.angle - 180) % 360)
            factors.extend(support_factors[(support in node.supports, support.constraints, orientation)])
        for beam in self.model.beams:
            beam_factors = self.generate_factors(self.beam_angle(node, beam))
            factors.extend(beam_factors[(beam in node.beams, 1, orientation)])
        return factors

    def get_node_forces(self, node: Node, orientation: Orientation) -> float:
        forces: List[float] = []
        for force in self.model.forces:
            force_factors = self.generate_factors(force.angle)
            forces.append(force_factors[(force in node.forces, 1, orientation)][0])
        return -sum(forces)

    def generate_factors(self, angle: float) -> Dict[Tuple[bool, int, Orientation], List[float]]:
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
        if beam in node.beams:
            other_node = beam.start_node if beam.start_node != node else beam.end_node
            return Line(Point(node.x, node.y), Point(other_node.x, other_node.y)).angle()
        return beam.angle

    def print_result(self):
        prefix_max_width = max(len(node.id) for node in self.model.nodes) + 8
        factors_max_width = max(len(self.format_float(f)) for row in self.factor_matrix for f in row)
        unknowns_max_width = max(len(force.id) for force in self.unknown_forces)
        result_max_width = max(len(self.format_float(f)) for f in self.result_vector)
        solved_max_width = max(len(self.format_float(f)) for f in self.solution_vector)

        center_index = len(self.unknown_forces) // 2
        for i in range(len(self.unknown_forces)):
            orientation = Orientation.HORIZONTAL if i % 2 == 0 else Orientation.VERTICAL
            prefix = f"({self.model.nodes[i // 2].id}, {orientation.value}) ".ljust(prefix_max_width)
            space1 = "   " if i != center_index else " x "
            space2 = "   " if i != center_index else " = "
            space3 = "    " if i != center_index else " -> "
            print(prefix + "[{}]".format(" ".join(self.format_float(factor).ljust(factors_max_width) for factor in self.factor_matrix[i])) 
                  + space1 + f"[{self.unknown_forces[i].id.ljust(unknowns_max_width)}]" 
                  + space2 + f"[{self.format_float(self.result_vector[i]).ljust(result_max_width)}]" 
                  + space3 + f"[{self.format_float(self.solution_vector[i]).ljust(solved_max_width)}]")

    def format_float(self, f) -> str:
        return "{:.2f}".format(f)