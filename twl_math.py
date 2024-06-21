import math
from enum import Enum


class Orientation(Enum):
    HORIZONTAL = "h"
    VERTICAL = "v"
    DIAGONAL = "d"


class Direction(Enum):
    CLOCKWISE = "clw"
    COUNTER_CLOCKWISE = "ccw"
    COLINEAR = "col"


class Point:
    def __init__(self, x: int, y: int):
        self.x: int = x
        self.y: int = y

    def rotate(self, center_of_rotation: 'Point', angle: float):
        angle %= 360
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

    def move(self, x: int, y: int):
        self.x += x
        self.y += y

    def subtract(self, other) -> 'Point':
        return Point(self.x - other.x, self.y - other.y)

    def dot_product(self, other) -> float:
        return self.x * other.x + self.y * other.y

    def distance_to_point(self, point: 'Point') -> float:
        return ((self.x - point.x) ** 2 + (self.y - point.y) ** 2) ** 0.5

    def distance_to_point_scaled(self, point: 'Point') -> float:
        return self.distance_to_point(point) * 0.01

    def distance_to_line(self, line: 'Line') -> float:
        p = line.end.subtract(line.start)
        norm = p.dot_product(p)

        u =  ((self.x - line.start.x) * p.x + (self.y - line.start.y) * p.y) / norm
        u = max(min(1, u), 0)

        dx = self.x - (line.start.x + u * p.x)
        dy = self.y - (line.start.y + u * p.y)

        return (dx*dx + dy*dy)**.5

    def distance_to_line_scaled(self, line: 'Line') -> float:
        return self.distance_to_line(line) * 0.01

    def scale(self, factor):
        self.x = self.x * factor
        self.y = self.y * factor

    def in_bounds(self, point_1: 'Point', point_2: 'Point'):
        min_x = min(point_1.x, point_2.x)
        max_x = max(point_1.x, point_2.x)
        min_y = min(point_1.y, point_2.y)
        max_y = max(point_1.y, point_2.y)

        return min_x <= self.x <= max_x and min_y <= self.y <= max_y


class Line:
    def __init__(self, start: Point, end: Point) -> None:
        self.start: Point = start
        self.end: Point = end

    def length(self) -> float:
        p = self.end.subtract(self.start)
        distance_squared = p.x**2 + p.y**2
        return math.sqrt(distance_squared)

    def length_scaled(self) -> float:
        return self.length() * 0.01

    def angle(self) -> float:
        d = self.end.subtract(self.start)
        angle_degrees = 90 - math.degrees(math.atan2(-d.y, d.x))
        angle_degrees %= 360
        return angle_degrees
    
    def angle_rounded(self) -> float:
        return (int((self.angle() + 22.5) // 45) * 45) % 360

    def distance(self, point: Point) -> float:
        return point.distance_to_line(self)

    def distance_scaled(self, point: Point) -> float:
        return point.distance_to_line_scaled(self)

    def rotate(self, center_of_rotation: Point, angle: float):
        [p.rotate(center_of_rotation, angle) for p in [self.start, self.end]]

    def move(self, x: int, y: int):
        self.start.move(x, y)
        self.end.move(x, y)

    def midpoint(self) -> Point:
        mid_x = (self.start.x + self.end.x) // 2
        mid_y = (self.start.y + self.end.y) // 2
        return Point(mid_x, mid_y)

    def resize(self, amount):
        length = self.length()
        if length > 0:
            if length + 2 * amount > 0:
                dx = (self.end.x - self.start.x) / length
                dy = (self.end.y - self.start.y) / length
                self.start = Point(self.start.x - amount * dx, self.start.y - amount * dy)
                self.end = Point(self.end.x + amount * dx, self.end.y + amount * dy)
            else:
                midpoint = self.midpoint()
                self.start = midpoint
                self.end = midpoint

    def slope(self) -> float | None:
        if self.end.x - self.start.x == 0:
            return None #line is vertical
        else:
            return (self.end.y - self.start.y) / (self.end.x - self.start.x)

    def perp_slope(self) -> float | None:
        original_slope = self.slope()
        if original_slope is None:
            return 0 #original line is vertical, return 0 for horizontal line
        elif original_slope == 0:
            return None #original line is horizontal, return None for vertical line
        else:
            return -1 / original_slope

    def y_intercept(self) -> float | None:
        slope = self.slope()
        if slope is None:
            return None
        else:
            return self.start.y - slope * self.start.x

    def closest_point_on_axis(self, point: Point) -> Point:
        slope = self.slope()
        perp_slope = self.perp_slope()
        if perp_slope is None:
            return Point(point.x, round(self.start.y))
        elif slope is None:
            return Point(round(self.start.x), point.y)
        else:
            y_intercept = self.y_intercept()
            assert(y_intercept)
            perp_y_intercept = point.y - perp_slope * point.x

            intersection_x = (y_intercept - perp_y_intercept) / (perp_slope - slope)
            intersection_y = slope * intersection_x + y_intercept
            return Point(round(intersection_x), round(intersection_y))

    def direction_to_point(self, point: Point) -> Direction:
        vector1 = (self.start.x - point.x, self.start.y - point.y)
        vector2 = (self.end.x - point.x, self.end.y - point.y)

        cross_product = vector1[0] * vector2[1] - vector1[1] * vector2[0]

        if cross_product > 0:
            return Direction.CLOCKWISE
        elif cross_product < 0:
            return Direction.COUNTER_CLOCKWISE
        else:
            return Direction.COLINEAR

    def scale(self, factor):
        self.start.scale(factor)
        self.end.scale(factor)


class Triangle:
    def __init__(self, p1: Point, p2: Point, p3: Point) -> None:
        self.p1: Point = p1
        self.p2: Point = p2
        self.p3: Point = p3

    def rotate(self, center_of_rotation: Point, angle: float):
        [p.rotate(center_of_rotation, angle) for p in [self.p1, self.p2, self.p3]]

    def scale(self, factor):
        self.p1.scale(factor)
        self.p2.scale(factor)
        self.p3.scale(factor)

    def barycentric_coordinates(self, point: Point) -> tuple[float, float, float]:
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

    def in_bounds(self, p1: Point, p2: Point) -> bool:
        return all(point.in_bounds(p1, p2) for point in self.points)

    def move(self, x: int, y: int):
        for point in self.points: 
            point.move(x, y)

    def midpoint(self):
        x = sum(point.x for point in self.points) / len(self.points)
        y = sum(point.y for point in self.points) / len(self.points)
        return Point(round(x), round(y))