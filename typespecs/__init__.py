__all__ = [
    # submodules
    "api",
    "spec",
    "typing",
    # aliases
    "ITSELF",
    "Spec",
    "from_annotated",
    "from_annotation",
    "from_annotations",
]
__version__ = "1.0.0"


# dependencies
from . import api, spec, typing
from .api import from_annotated, from_annotation, from_annotations
from .spec import ITSELF, Spec
