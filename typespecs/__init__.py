__all__ = [
    # submodules
    "core",
    "frame",
    "typing",
    # aliases
    "ITSELF",
    "ItselfType",
    "Spec",
    "SpecFrame",
    "from_annotated",
    "from_annotation",
    "from_annotations",
]
__version__ = "5.0.0"


# dependencies
from . import core, frame, typing
from .core import (
    ITSELF,
    ItselfType,
    Spec,
    from_annotated,
    from_annotation,
    from_annotations,
)
from .frame import SpecFrame
