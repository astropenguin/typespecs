__all__ = [
    "Spec",
    "api",
    "from_dataclass",
    "from_typehint",
    "is_spec",
    "spec",
    "typing",
]
__version__ = "0.3.0"


# dependencies
from . import api
from . import spec
from . import typing
from .api import from_dataclass, from_typehint
from .spec import Spec, is_spec
