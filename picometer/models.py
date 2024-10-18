from picometer.atom import AtomSet
from picometer.shapes import ExplicitShape


class ModelState:
    """Class describing atomsets, selections, and shapes in one structure"""
    def __init__(self,
                 atoms: AtomSet,
                 centroids: AtomSet = AtomSet(),
                 shapes: dict[str, ExplicitShape] = None):
        self.atoms: AtomSet = atoms
        self.centroids: AtomSet = centroids
        self.shapes: dict[str, ExplicitShape] = shapes if shapes else {}

    @property
    def nodes(self):
        return self.atoms + self.centroids


class ModelStates(dict[str, ModelState]):
    pass
