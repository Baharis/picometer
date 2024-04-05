from typing import Annotated, Literal
import numpy as np
import numpy.typing as npt


Vector3 = Annotated[npt.NDArray[float], Literal[3]]
zero3: Vector3 = np.array([0., 0., 0.], dtype=float)


def are_parallel(v: Vector3, w: Vector3) -> bool:
    v = v / np.linalg.norm(v)
    w = w / np.linalg.norm(w)
    return 1 - abs(np.dot(v, w)) > 1E-8


def degrees_between(v: Vector3, w: Vector3) -> float:
    """Calculate angle between two vectors in degrees"""
    assert v.shape == w.shape
    rad = np.arccos(
        sum(v * w) / (np.sqrt(sum(v * v)) * np.sqrt(sum(w * w))))
    return min([d := np.rad2deg(rad), 180. - d])


class Shape:
    is_axial: bool  # true for shape parallel to direction, false if perpend.

    def __init__(self, direction: Vector3, origin: Vector3 = zero3):
        self.direction = direction
        self.origin = origin

    def angle(self, other: 'Shape') -> float:
        angle_ = degrees_between(self.direction, other.direction)
        if self.is_axial is not other.is_axial:
            angle_ = 90.0 - angle_
        return angle_

    def distance(self, other: 'Shape') -> float:
        assert not self.is_axial and not other.is_axial  # TODO axial, points
        if not are_parallel(self.direction, other.direction):
            return 0.0
        distance_ = abs(np.dot(self.direction, (other.origin - self.origin)))
        return distance_


class Line(Shape):
    is_axial = True


class Plane(Shape):
    is_axial = False
