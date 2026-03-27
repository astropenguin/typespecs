__all__ = [
    # submodules
    "api",
    "spec",
    "typing",
    "utils",
    # aliases
    "ITSELF",
    "Spec",
    "SpecFrame",
    "from_annotated",
    "from_annotation",
    "from_annotations",
]
__version__ = "2.0.2"


# dependencies
from . import api, spec, typing, utils
from .api import from_annotated, from_annotation, from_annotations
from .spec import ITSELF, Spec, SpecFrame
