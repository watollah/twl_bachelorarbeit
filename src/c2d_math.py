import math
from enum import Enum


class Orientation(Enum):
    """Represents orientation in the Model. Possible values are: HORIZONTAL, VERTICAL or DIAGONAL."""
    HORIZONTAL = "h"
    VERTICAL = "v"
    DIAGONAL = "d"


class Direction(Enum):
    """Represents direction in the Model. Possible values are: CLOCKWISE, COUNTER_CLOCKWISE or COLINEAR."""
    CLOCKWISE = "clw"
    COUNTER_CLOCKWISE = "ccw"
    COLINEAR = "col"


class Point:
    """Stores xy coordinate as two float values."""

    def __init__(self, x: float, y: float):
        """Create an instance of Point."""
        self.x: float = x
        self.y: float = y

    def rotate(self, center_of_rotation: 'Point', angle: float):
        """Rotate the Point around a specified center of rotation."""
        angle %= 360
        angle = math.radians(angle)

        #Translate the Point to be rotated so that the center of rotation becomes the origin
        translated_x = self.x - center_of_rotation.x
        translated_y = self.y - center_of_rotation.y
        
        #Rotate the translated Point around the origin by the specified angle
        rotated_x = translated_x * math.cos(angle) - translated_y * math.sin(angle)
        rotated_y = translated_x * math.sin(angle) + translated_y * math.cos(angle)
        
        #Translate the rotated Point back to its original position
        self.x = rotated_x + center_of_rotation.x
        self.y = rotated_y + center_of_rotation.y

    def move(self, x: float, y: float):
        """Move the Point by the specified amount in x and y direction."""
        self.x += x
        self.y += y

    def subtract(self, other) -> 'Point':
        """Subtract the Points from each other."""
        return Point(self.x - other.x, self.y - other.y)

    def dot_product(self, other) -> float:
        """Take the dot product of the two Points."""
        return self.x * other.x + self.y * other.y

    def distance_to_point(self, point: 'Point') -> float:
        """Returns the distance of between this Point and the specified Point."""
        return ((self.x - point.x) ** 2 + (self.y - point.y) ** 2) ** 0.5

    def distance_to_point_scaled(self, point: 'Point') -> float:
        """Return the distance between this point and the specified Point, scaled by a factor of 0.01."""
        return self.distance_to_point(point) * 0.01

    def distance_to_line(self, line: 'Line') -> float:
        """Return the shortest distance between this Point and the Line."""
        p = line.end.subtract(line.start)
        norm = p.dot_product(p)

        u =  ((self.x - line.start.x) * p.x + (self.y - line.start.y) * p.y) / norm
        u = max(min(1, u), 0)

        dx = self.x - (line.start.x + u * p.x)
        dy = self.y - (line.start.y + u * p.y)

        return (dx*dx + dy*dy)**.5

    def distance_to_line_scaled(self, line: 'Line') -> float:
        """Return the shortest distance between this Point and the Line scaled by a factor of 0.01."""
        return self.distance_to_line(line) * 0.01

    def scale(self, factor):
        """Scale the coordinates of this Point by the specified factor."""
        self.x = self.x * factor
        self.y = self.y * factor

    def in_bounds(self, point_1: 'Point', point_2: 'Point'):
        """Check if this Point is within the bounds defined as a rectangle 
        from point_1 in the top left corner to point_2 in the bottom right corner."""
        min_x = min(point_1.x, point_2.x)
        max_x = max(point_1.x, point_2.x)
        min_y = min(point_1.y, point_2.y)
        max_y = max(point_1.y, point_2.y)

        return min_x <= self.x <= max_x and min_y <= self.y <= max_y


class Line:
    """Line defined by two Points start and end."""

    def __init__(self, start: Point, end: Point) -> None:
        """Create an instance of Line."""
        self.start: Point = start
        self.end: Point = end

    def length(self) -> float:
        """Returns the length of this Line."""
        p = self.end.subtract(self.start)
        distance_squared = p.x**2 + p.y**2
        return math.sqrt(distance_squared)

    def length_scaled(self) -> float:
        """Returns the length of this Line scaled by a factor of 0.01."""
        return self.length() * 0.01

    def set_length(self, length):
        """Set the length of this Line by keeping the start Point and direction and moving the end Point."""
        direction = self.end.subtract(self.start)
        ux = direction.x / self.length()
        uy = direction.y / self.length()
        self.end.x = self.start.x + (ux * length * 100)
        self.end.y = self.start.y + (uy * length * 100)

    def angle(self) -> float:
        """Returns the angle of this Line in degrees."""
        d = self.end.subtract(self.start)
        angle_degrees = 90 - math.degrees(math.atan2(-d.y, d.x))
        angle_degrees %= 360
        return angle_degrees

    def angle_rounded(self) -> float:
        """Returns the angle of this Line in degrees rounded in steps of 45."""
        return (round((self.angle() + 22.5) // 45) * 45) % 360

    def distance(self, point: Point) -> float:
        """Returns the shortest distance between this Line and the specified Point."""
        return point.distance_to_line(self)

    def distance_scaled(self, point: Point) -> float:
        """Returns the shortest distance between this Line and the specified Point scaled by a factor of 0.01."""
        return point.distance_to_line_scaled(self)

    def rotate(self, center_of_rotation: Point, angle: float):
        """Rotate this Line around the specified center of rotation by rotating it's start and end Points."""
        [p.rotate(center_of_rotation, angle) for p in [self.start, self.end]]

    def move(self, x: float, y: float):
        """Move this Line by the specified amount in x and y direction by moving it's start and end Points."""
        self.start.move(x, y)
        self.end.move(x, y)

    def midpoint(self) -> Point:
        """Returns the midpoint of this Line."""
        mid_x = (self.start.x + self.end.x) / 2
        mid_y = (self.start.y + self.end.y) / 2
        return Point(mid_x, mid_y)

    def resize(self, amount):
        """Resize this Line by keeping it's direction but shrinking or expanding it by the specified amount at both ends."""
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
        """Returns the slope of this Line."""
        if self.end.x - self.start.x == 0:
            return None #Line is vertical
        else:
            return (self.end.y - self.start.y) / (self.end.x - self.start.x)

    def perp_slope(self) -> float | None:
        """Returns the perpendicular slope of this Line."""
        original_slope = self.slope()
        if original_slope is None:
            return 0 #original Line is vertical, return 0 for horizontal Line
        elif original_slope == 0:
            return None #original Line is horizontal, return None for vertical Line
        else:
            return -1 / original_slope

    def y_intercept(self) -> float | None:
        """Returns the y intercept for this Line."""
        slope = self.slope()
        if slope is None:
            return None
        else:
            return self.start.y - slope * self.start.x

    def closest_point(self, point: Point) -> Point:
        """Returns the closest Point on this Line to the specified Point."""
        slope = self.slope()
        perp_slope = self.perp_slope()
        if perp_slope is None:
            return Point(point.x, self.start.y)
        elif slope is None:
            return Point(self.start.x, point.y)
        else:
            y_intercept = self.y_intercept()
            assert(y_intercept)
            perp_y_intercept = point.y - perp_slope * point.x

            intersection_x = (y_intercept - perp_y_intercept) / (perp_slope - slope)
            intersection_y = slope * intersection_x + y_intercept
            return Point(intersection_x, intersection_y)

    def direction_to_point(self, point: Point) -> Direction:
        """Returns the direct of this Line relative to the specified Point."""
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
        """Scale this Line by a factor by scaling the start and end Point."""
        self.start.scale(factor)
        self.end.scale(factor)

    def intersects(self, line: 'Line') -> bool:
        """Returns True if this Line intersects the specified Line, False otherwise."""
        a = (line.end.x - line.start.x) * (line.start.y - self.start.y) - (line.end.y - line.start.y) * (line.start.x - self.start.x)
        b = (line.end.x - line.start.x) * (self.end.y - self.start.y) - (line.end.y - line.start.y) * (self.end.x - self.start.x)
        c = (self.end.x - self.start.x) * (line.start.y - self.start.y) - (self.end.y - self.start.y) * (line.start.x - self.start.x)
        return False if b == 0 else 0 < (a / b) < 1 and 0 < (c / b) < 1


class Triangle:
    """Triangle defined by three Points p1, p2 and p3."""

    def __init__(self, p1: Point, p2: Point, p3: Point) -> None:
        """Create an instance of Triangle."""
        self.p1: Point = p1
        self.p2: Point = p2
        self.p3: Point = p3

    def rotate(self, center_of_rotation: Point, angle: float):
        """Rotate the Triangle by rotating all of it's Points."""
        [p.rotate(center_of_rotation, angle) for p in [self.p1, self.p2, self.p3]]

    def scale(self, factor):
        """Scale the Triangle by scaling all of it's Points."""
        self.p1.scale(factor)
        self.p2.scale(factor)
        self.p3.scale(factor)

    def barycentric_coordinates(self, point: Point) -> tuple[float, float, float]:
        """Returns the barycentric coordinates of the specified Point in this Triangle."""
        v0 = self.p2.subtract(self.p1)
        v1 = self.p3.subtract(self.p1)
        v2 = point.subtract(self.p1)

        dot00 = v0.dot_product(v0)
        dot01 = v0.dot_product(v1)
        dot02 = v0.dot_product(v2)
        dot11 = v1.dot_product(v1)
        dot12 = v1.dot_product(v2)

        inv_denom = 1 / (dot00 * dot11 - dot01 * dot01)
        u = (dot11 * dot02 - dot01 * dot12) * inv_denom
        v = (dot00 * dot12 - dot01 * dot02) * inv_denom
        w = 1 - u - v

        return (u, v, w)

    def inside_triangle(self, point: Point) -> bool:
        """Returns True if the point is inside the triangle, False otherwise."""
        bc = self.barycentric_coordinates(point)
        return bc[0] >= 0 and bc[1] >= 0 and bc[2] >= 0 and bc[0] + bc[1] + bc[2] <= 1


class Polygon:
    """Polygon defined by a list of Points."""

    def __init__(self, *points: Point) -> None:
        """Create an instance of Polygon."""
        self.points: list[Point] = list(points)
        
    @classmethod
    def from_list(cls, point_list: list[Point]) -> 'Polygon':
        """Returns a Polygon created from the list of Points."""
        return cls(*point_list)

    def in_bounds(self, p1: Point, p2: Point) -> bool:
        """Returns True if all Points of the Polygon are within the bounds of the rectangle defined by the specified Points."""
        return all(point.in_bounds(p1, p2) for point in self.points)

    def move(self, x: float, y: float):
        """Move the Polygon by the specified amount in x and y direction by moving all of it's Points."""
        for point in self.points: 
            point.move(x, y)

    def midpoint(self) -> Point:
        """Returns the midpoint of this Polygon, calculated as the average position of all it's Points."""
        x = sum(point.x for point in self.points) / len(self.points)
        y = sum(point.y for point in self.points) / len(self.points)
        return Point(x, y)