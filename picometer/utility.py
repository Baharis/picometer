from typing import Iterable, List

import numpy as np
import uncertainties as uc
import uncertainties.unumpy as unp


def norm(values: np.ndarray) -> uc.UFloat:
    return unp.sqrt(sum(values * values))


def ustr2float(s: str) -> float:
    """Convert a string "1.23(4)" to float `1.23`, stripping uncertainty."""
    return uc.ufloat_fromstr(s).nominal_value


def ustr2floats(s: Iterable[str]) -> List[float]:
    """Convenience function to convert an iterable of u-strings to floats."""
    return [ustr2float(s) for s in s]

def ustr2ufloats(s: Iterable[str]) -> List[uc.UFloat]:
    """Convenience function to convert an iterable of u-strings to floats."""
    return [uc.ufloat_fromstr(_) for _ in s]
