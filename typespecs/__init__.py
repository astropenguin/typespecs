__all__ = [
    # submodules
    "core",
    "mapping",
    "typing",
    # aliases
    "ITSELF",
    "Config",
    "Consts",
    "Spec",
    "from_annotated",
    "from_annotation",
    "from_annotations",
]
__version__ = "11.0.1"


# dependencies
from . import core, mapping, typing
from .core import *

# constants
ITSELF = Consts.ITSELF
"""Sentinel for specifying metadata-stripped annotation itself."""
