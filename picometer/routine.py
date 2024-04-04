from collections import deque, UserDict


class Routine(UserDict):
    """A set of individual instructions to be performed in processor"""


class RoutineQueue(deque[Routine]):
    """A queue of individual routines to be performed sequentially"""
