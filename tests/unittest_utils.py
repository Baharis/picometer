from functools import partialmethod
from unittest import TestCase


class TestCaseExtras:
    """A TestCase mix-in with shorthands for existing tests"""

    assertNumericallyEqual = partialmethod(TestCase.assertAlmostEqual, places=12)
    """A variant of `self.assertAlmostEqual` with stricter places default"""
