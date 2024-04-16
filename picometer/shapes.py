import copy
import enum
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
    class Kind(enum.Enum):
        axial = 1  # spans in 1D along direction
        planar = 2  # spans in 2D perpendicular to direction
        spatial = 3  # spans in 0D or 3D, irrelevant direction

    kind: Kind
    direction: Vector3
    origin: Vector3

    def __repr__(self):
        name = self.__class__.__name__
        return f'{name}(direction={self.direction}, origin={self.origin})'

    def at(self, origin: Vector3) -> 'Shape':
        """Return a copy of self with centroid at new origin"""
        new = copy.deepcopy(self)
        new.origin = np.array(origin, dtype=float)
        return new

    def angle(self, other: 'Shape') -> float:
        kinds = {self.kind, other.kind}
        assert self.Kind.spatial not in kinds, 'No angle: directionless'
        angle_ = degrees_between(self.direction, other.direction)
        if len(kinds) == 2:
            angle_ = 90.0 - angle_
        return angle_

    def distance(self, other: 'Shape') -> float:
        assert all(x.kind is self.Kind.planar for x in [self, other])
        # TODO implement distances for shapes other than planes
        if not are_parallel(self.direction, other.direction):
            return 0.0
        distance_ = abs(np.dot(self.direction, (other.origin - self.origin)))
        return distance_


class ExplicitShape(Shape):
    def __init__(self, direction: Vector3, origin: Vector3 = zero3):
        self.direction = direction
        self.origin = origin


class Line(ExplicitShape):
    kind = Shape.Kind.axial


class Plane(ExplicitShape):
    kind = Shape.Kind.planar
