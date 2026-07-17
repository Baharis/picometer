# read version from installed package
from importlib.metadata import PackageNotFoundError, version


try:
    __version__ = version('picometer')
except PackageNotFoundError:
    __version__ = '0+unknown'
