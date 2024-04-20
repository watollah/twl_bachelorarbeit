import math

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


class Polygon:
    def __init__(self, *points: Point) -> None:
        self.points: list[Point] = list(points)
        
    @classmethod
    def from_list(cls, point_list: list[Point]) -> 'Polygon':
        return cls(*point_list)