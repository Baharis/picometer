import unittest

import numpy as np

from picometer.shapes import are_parallel, are_perpendicular,\
    degrees_between, Line, Plane, zero3

v_a = np.array([1.0, 2.0, 3.0], dtype=float)
v_b = np.array([1.0, 2.0, -3.0], dtype=float)    # 106.602 degrees rel. to v_a
v_c = np.array([0.0, -3.0, 2.0], dtype=float)    # perpendicular to v_a
v_d = np.array([-1.0, -2.0, -3.0], dtype=float)  # (anti)parallel to v_a
ab_degrees = 106.60154959902023


class TestVectorTools(unittest.TestCase):
    def test_are_parallel(self) -> None:
        self.assertFalse(are_parallel(v_a, v_b))
        self.assertFalse(are_parallel(v_a, v_c))
        self.assertTrue(are_parallel(v_a, v_d))

    def test_are_perpendicular(self) -> None:
        self.assertFalse(are_perpendicular(v_a, v_b))
        self.assertTrue(are_perpendicular(v_a, v_c))
        self.assertFalse(are_perpendicular(v_a, v_d))

    def test_degrees_between(self) -> None:
        self.assertEqual(degrees_between(v_a, v_b), ab_degrees)
        self.assertEqual(degrees_between(v_a, v_c), 90.0)
        self.assertEqual(degrees_between(v_a, v_d), 180.0)
        self.assertEqual(degrees_between(v_a, v_b, True), 180. - ab_degrees)
        self.assertEqual(degrees_between(v_a, v_c, normalize=True), 90.0)
        self.assertEqual(degrees_between(v_a, v_d, normalize=True), 0.0)


class TestExplicitShapes(unittest.TestCase):
    def test_line_line_metrics(self):
        line_a = Line(direction=v_a, origin=v_b)
        line_b = Line(direction=v_b, origin=zero3)
        line_c = Line(direction=v_c, origin=zero3)
        line_d = Line(direction=v_d, origin=zero3)
        self.assertEqual(line_a.distance(line_b), 0.)
        self.assertEqual(line_a.distance(line_c), 1.3342487699899823)
        self.assertEqual(line_a.distance(line_d), 3.5856858280031814)
        self.assertEqual(line_a.angle(line_b), 180. - ab_degrees)
        self.assertEqual(line_a.angle(line_c), 90.)
        self.assertEqual(line_a.angle(line_d), 0.)

    def test_line_plane_metrics(self):
        line_a = Line(direction=v_a, origin=v_b)
        plane_b = Plane(direction=v_b, origin=zero3)
        plane_c = Plane(direction=v_c, origin=zero3)
        plane_d = Plane(direction=v_d, origin=zero3)
        self.assertEqual(line_a.distance(plane_b), 0.)
        self.assertEqual(line_a.distance(plane_c), 3.328201177351375)
        self.assertEqual(line_a.distance(plane_d), 0.)
        self.assertEqual(line_a.angle(plane_b), ab_degrees - 90.)
        self.assertEqual(line_a.angle(plane_c), 0.)
        self.assertEqual(line_a.angle(plane_d), 90.)

    def test_plane_plane_metrics(self):
        plane_a = Plane(direction=v_a, origin=v_b)
        plane_b = Plane(direction=v_b, origin=zero3)
        plane_c = Plane(direction=v_c, origin=zero3)
        plane_d = Plane(direction=v_d, origin=zero3)
        self.assertEqual(plane_a.distance(plane_b), 0.)
        self.assertEqual(plane_a.distance(plane_c), 0.)
        self.assertEqual(plane_a.distance(plane_d), 1.0690449676496976)
        self.assertEqual(plane_a.angle(plane_b), 180. - ab_degrees)
        self.assertEqual(plane_a.angle(plane_c), 90.)
        self.assertEqual(plane_a.angle(plane_d), 0.)

    def test_line_plane_at(self):
        line = Line(direction=v_a, origin=v_b)
        plane = Plane(direction=v_c, origin=v_d)
        self.assertEqual(line.distance(plane), 3.328201177351375)
        line = line.at(origin=-v_c)
        self.assertEqual(line.distance(plane), 3.6055512754639896)
        line = line.at(origin=zero3)
        self.assertEqual(line.distance(plane), 0.)
        plane = plane.at(v_c)
        self.assertEqual(line.distance(plane), 3.6055512754639896)
