"""
Algorithm:
* Double the number of points, inserting additional points between vertices
* Iterate from first point to number of points / 2
== prepare shape ==
** Select the point (pf)
** Translate the shape so pf is at 0,0
** Pick the opposite point (po)
** Calculate the angle of po
** Rotate shape so po.y is at 0
== Check if mirror image of shape along X axis matches ==
** Iterate points on either side of pf towards po (pi_top, pi_bottom)
*** compare absolute value of y coordinate of pi_top and pi_bottom. If they equal, then the pair of points match
*** If all coordinates pairs match, the line between pf and po is a line of symmetry
*** stash this in our list of symmetries
"""
from copy import deepcopy
import math
from typing import Callable, List, Optional, Set

class Point:
    pass

class Point:
    """
    Stores a point by x and y coordinates
    """

    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    def __copy__(self) -> Point:
        return Point(self.x, self.y)

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return f"({self.x},{self.y})"


class Symmetry:
    """
    Detects lines of symmetry for the specified shape
    """

    # How close matching pixels need to be
    CLOSE_ENOUGH = 5

    def __init__(
        self,
        points: List[Point],
        original_callback: Optional[Callable[[int, List[Point]], None]] = None,
        translate_callback: Optional[Callable[[int, List[Point]], None]] = None,
        rotate_callback: Optional[Callable[[int, List[Point]], None]] = None,
        symmetry_callback: Optional[Callable[[int, Point, Point], None]] = None,
    ) -> None:
        self._points = points
        self._original_callback = original_callback
        self._translate_callback = translate_callback
        self._rotate_callback = rotate_callback
        self._symmetry_callback = symmetry_callback

    def _translate_shape(self, points: List[Point], dx: float, dy: float) -> None:
        for pc in points:
            pc.x -= dx
            pc.y -= dy

    def _get_distance(self, p1: Point, p2: Point) -> float:
        return (((p2.x - p1.x) ** 2) + ((p2.y - p1.y) ** 2)) ** 0.5

    def _get_angle(self, p1: Point, p2: Point) -> float:
        return -math.degrees(math.atan2(p2.y - p1.y, p2.x - p1.x))

    def _get_midpoint(self, p1: Point, p2: Point) -> Point:
        return Point((p1.x + p2.x) / 2, (p1.y + p2.y) / 2)

    def _points_really_close(self, p1: Point, p2: Point) -> bool:
        return self._get_distance(p1, p2) < Symmetry.CLOSE_ENOUGH

    def _rotate_point(self, p: Point, angle: float) -> None:
        angle = math.radians(angle)
        new_x = p.x * math.cos(angle) - p.y * math.sin(angle)
        new_y = p.x * math.sin(angle) + p.y * math.cos(angle)
        p.x = new_x
        p.y = new_y

    def _double_points(self, points: List[Point]) -> List[Point]:
        doubled_points = []
        previous_point = None
        for point in points:
            if previous_point:
                doubled_points.append(self._get_midpoint(previous_point, point))
            doubled_points.append(point)
            previous_point = point
        if previous_point:
            doubled_points.append(self._get_midpoint(previous_point, points[0]))
        return doubled_points

    def get_lines_of_symmetry(self) -> List[List[Point]]:
        points = self._points
        symmetries = []

        # double the number of points by inserting mid-line points
        points = self._double_points(points)
        length = len(points)

        half_length = int(length / 2)

        for index in range(half_length):
            if self._original_callback:
                self._original_callback(index, points)

            # make a working copy of the points
            points_copy = deepcopy(points)
            pf = points_copy[index]

            # move shape so pf is at (0,0)
            self._translate_shape(points_copy, pf.x, pf.y)

            # notifiy anyone who cares
            if self._translate_callback:
                self._translate_callback(index, points_copy)

            # figure out the opposite point symmetry line
            opposite_index = index + half_length
            po = points_copy[opposite_index]

            # Rotate shape so po.y = 0
            angle = self._get_angle(pf, po)
            for p in points_copy:
                self._rotate_point(p, angle)

            # Notify anyone who cares
            if self._rotate_callback:
                self._rotate_callback(index, points_copy)

            # now check if other side of the symmetry line is a mirror image
            symmetrical = True
            for mirror_index in range(half_length):
                mirror1_point = points_copy[index - mirror_index]
                mirror2_point = points_copy[index + mirror_index]
                if not self._points_really_close(
                    Point(mirror1_point.x, abs(mirror1_point.y)),
                    Point(mirror2_point.x, abs(mirror2_point.y)),
                ):
                    symmetrical = False

            if symmetrical:
                # Get the original symmetry points and stash
                symmetry_point1 = points[index]
                symmetry_point2 = points[opposite_index]
                symmetries.append([symmetry_point1, symmetry_point2])

                # Notify anyone who cares
                if self._symmetry_callback:
                    self._symmetry_callback(index, symmetry_point1, symmetry_point2)

        return symmetries
