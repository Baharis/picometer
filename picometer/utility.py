from typing import Iterable, List

import uncertainties as uc


def ustr2float(s: str) -> float:
    """Convert a string "1.23(4)" to float `1.23`, stripping uncertainty."""
    return uc.ufloat_fromstr(s).nominal_value


def ustr2floats(s: Iterable[str]) -> List[float]:
    """Convenience function to convert an iterable of u-strings to floats."""
    return [ustr2float(s) for s in s]
