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
]
__version__ = "0.5.0"


# dependencies
from . import api, spec, typing
from .api import from_annotated, from_annotation
from .spec import ITSELF, Spec
