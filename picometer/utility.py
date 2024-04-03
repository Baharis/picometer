import uncertainties as uc


def ustr2float(s: str) -> float:
    return uc.ufloat_fromstr(s).nominal_value
