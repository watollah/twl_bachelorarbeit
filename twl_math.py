import math
from typing import Tuple

class Point:
    def __init__(self, x: int, y: int):
        self.x: int = x
        self.y: int = y

    def rotate(self, center_of_rotation: 'Point', angle: float):
        angle = math.radians(angle)

        #Translate the point to be rotated so that the center of rotation becomes the origin
        translated_x = self.x - center_of_rotation.x
        translated_y = self.y - center_of_rotation.y
        
        #Rotate the translated point around the origin by the specified angle
        rotated_x = int(translated_x * math.cos(angle) - translated_y * math.sin(angle))
        rotated_y = int(translated_x * math.sin(angle) + translated_y * math.cos(angle))
        
        #Translate the rotated point back to its original position
        self.x = rotated_x + center_of_rotation.x
        self.y = rotated_y + center_of_rotation.y

    def subtract(self, other) -> 'Point':
        return Point(self.x - other.x, self.y - other.y)

    def dot_product(self, other) -> float:
        return self.x * other.x + self.y * other.y

    def distance(self, line: 'Line') -> float:
        p = line.end.subtract(line.start)
        norm = p.dot_product(p)

        u =  ((self.x - line.start.x) * p.x + (self.y - line.start.y) * p.y) / norm
        u = max(min(1, u), 0)

        dx = self.x - (line.start.x + u * p.x)
        dy = self.y - (line.start.y + u * p.y)

        return (dx*dx + dy*dy)**.5


class Line:
    def __init__(self, start: Point, end: Point) -> None:
        self.start: Point = start
        self.end: Point = end

    def length(self) -> float:
        p = self.end.subtract(self.start)
        distance_squared = p.x**2 + p.y**2
        return math.sqrt(distance_squared)

    def angle(self) -> float:
        d = self.end.subtract(self.start)
        angle_degrees = 90 - math.degrees(math.atan2(-d.y, d.x))
        angle_degrees %= 360
        return angle_degrees

    def distance(self, point: Point) -> float:
        return point.distance(self)


class Triangle:
    def __init__(self, p1: Point, p2: Point, p3: Point) -> None:
        self.p1: Point = p1
        self.p2: Point = p2
        self.p3: Point = p3

    def rotate(self, center_of_rotation: Point, angle: float):
        [p.rotate(center_of_rotation, angle) for p in [self.p1, self.p2, self.p3]]

    def barycentric_coordinates(self, point: Point) -> Tuple[float, float, float]:
        v0 = self.p2.subtract(self.p1)
        v1 = self.p3.subtract(self.p1)
        v2 = point.subtract(self.p1)

        dot00 = v0.dot_product(v0)
        dot01 = v0.dot_product(v1)
        dot02 = v0.dot_product(v2)
        dot11 = v1.dot_product(v1)
        dot12 = v1.dot_product(v2)

        # Compute barycentric coordinates
        inv_denom = 1 / (dot00 * dot11 - dot01 * dot01)
        u = (dot11 * dot02 - dot01 * dot12) * inv_denom
        v = (dot00 * dot12 - dot01 * dot02) * inv_denom
        w = 1 - u - v

        return (u, v, w)

    def inside_triangle(self, point: Point) -> bool:
        bc = self.barycentric_coordinates(point)
        return bc[0] >= 0 and bc[1] >= 0 and bc[2] >= 0 and bc[0] + bc[1] + bc[2] <= 1


class Polygon:
    def __init__(self, *points: Point) -> None:
        self.points: list[Point] = list(points)
        
    @classmethod
    def from_list(cls, point_list: list[Point]) -> 'Polygon':
        return cls(*point_list)