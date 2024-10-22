import abc
import copy
import enum
import logging
from typing import Annotated, Literal, Protocol, Union

import numpy as np
import numpy.typing as npt
from numpy.linalg import norm


logger = logging.getLogger(__name__)


Vector3 = Annotated[npt.NDArray[float], Literal[3]]
Versor3 = Annotated[npt.NDArray[float], Literal[3]]
zero3: Vector3 = np.array([0., 0., 0.], dtype=float)


class AtomSet(Protocol):
    cart_xyz: np.ndarray


def are_parallel(v: Vector3, w: Vector3) -> bool:
    """Check if input vectors point along the same line in any direction"""
    return 1 - abs(np.dot(v / norm(v), w / norm(w))) < 1E-8


def are_synparallel(v: Vector3, w: Vector3) -> bool:
    """Check if input vectors point along the same line in the same direction"""
    return 1 - np.dot(v / norm(v), w / norm(w)) < 1E-8


def are_antiparallel(v: Vector3, w: Vector3) -> bool:
    """Check if input vectors point along the same line in opposite directions"""
    return 1 + np.dot(v / norm(v), w / norm(w)) < 1E-8


def are_perpendicular(v: Vector3, w: Vector3) -> bool:
    """Check in input vectors are perpendicular"""
    return abs(norm(v) * norm(w) - norm(np.cross(v, w))) < 1E-8


def versorize(v: Vector3) -> Versor3:
    """Normalize and choose lexicographically-larger of antiparallel v and -v"""
    assert isinstance(v, np.ndarray) and np.shape(v) == (3, )
    assert (v_norm := np.linalg.norm(v)) > 0
    neg = v[0] < 0 or (v[0] == 0 and (v[1] < 0 or (v[1] == 0 and v[2] < 0)))
    return (-v if neg else v) / v_norm


def degrees_between(v: Vector3, w: Vector3, normalize: bool = False) -> float:
    """Calculate angle between two vectors in degrees"""
    assert v.shape == w.shape
    rad = np.arccos(
        sum(v * w) / (np.sqrt(sum(v * v)) * np.sqrt(sum(w * w))))
    deg = np.rad2deg(rad)
    return 180. - deg if deg > 90. and normalize else deg


class Shape:
    class Kind(enum.Enum):
        axial = 1  # spans in 1D along direction
        planar = 2  # spans in 2D perpendicular to direction
        spatial = 3  # spans in 0D or 3D, irrelevant direction

    kind: Kind
    direction: Versor3
    origin: Vector3

    def __repr__(self):
        name = self.__class__.__name__
        return f'{name}(direction={self.direction}, origin={self.origin})'

    def at(self, origin: Vector3) -> 'Shape':
        """Return a copy of self with centroid at new origin"""
        new = copy.deepcopy(self)
        new.origin = np.array(origin, dtype=float)
        return new

    @abc.abstractmethod
    def _distance(self, other: 'Shape') -> float:
        pass

    def distance(self, other: 'Shape') -> float:
        """
        Delegated to a concrete implementation.
        Since self.kind >= other.kind, concrete implementations need only
        to handle shapes of equal of lower kind.
        """
        assert isinstance(self, Shape) and isinstance(other, Shape)
        if not self.kind.value >= other.kind.value:  # let self.kind >= other
            return other.distance(self)
        logger.debug(f'Calculating distance between {self} and {other}')
        return self._distance(other)  # delegate to concrete implementation

    @abc.abstractmethod
    def _angle(self, other: 'Shape') -> float:
        pass

    def angle(self, *others: 'Shape') -> float:
        """
        Delegated to a concrete implementation.
        For Explicit shape, accept two parameters; for AtomSets, any size.
        """
        assert all(isinstance(o, Shape) for o in [self, *others])
        logger.debug(f'Calculating angle between {self} and {others}')
        return self._angle(*others)  # delegate to concrete implementation


class ExplicitShape(Shape, abc.ABC):
    def __init__(self, direction: Vector3, origin: Vector3 = zero3):
        self.direction = direction
        self.origin = origin

    @property
    def direction(self) -> Versor3:
        return self._direction

    @direction.setter
    def direction(self, vector: Vector3) -> None:
        self._direction = versorize(vector)

    def _angle(self, *others: 'Shape') -> float:
        assert len(others) == 1, 'Handle only angles between 2 ExplicitShapes'
        other = others[0]
        deg = degrees_between(self.direction, other.direction, normalize=True)
        return deg if self.kind is others[0].kind else 90.0 - deg


class Line(ExplicitShape):
    kind = Shape.Kind.axial

    def _distance(self, other: 'Line'):
        delta = other.origin - self.origin
        if are_parallel(self.direction, other.direction):
            d = self.direction
            return np.linalg.norm(delta - (np.dot(d, delta) * d))
        else:
            shortest_direction = np.cross(self.direction, other.direction)
            return abs(np.dot(delta, shortest_direction))


class Plane(ExplicitShape):
    kind = Shape.Kind.planar

    def _distance(self, other: Union[Line, 'Plane']) -> float:
        delta = other.origin - self.origin
        dont_intersect_cond = are_parallel \
            if other.kind is self.Kind.planar else are_perpendicular
        dont_intersect = dont_intersect_cond(self.direction, other.direction)
        return abs(np.dot(delta, self.direction)) if dont_intersect else 0.0
