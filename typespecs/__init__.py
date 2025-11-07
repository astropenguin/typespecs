__all__ = [
    "Spec",
    "SpecFrame",
    "api",
    "from_dataclass",
    "from_typehint",
    "spec",
    "typing",
]
__version__ = "0.4.0"


# dependencies
from . import api, spec, typing
from .api import from_dataclass, from_typehint
from .spec import Spec, SpecFrame
