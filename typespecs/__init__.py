__all__ = [
    "Attrs",
    "api",
    "from_dataclass",
    "from_typehint",
    "is_attrs",
    "typing",
]
__version__ = "0.2.0"


# dependencies
from . import api
from . import typing
from .api import Attrs, from_dataclass, from_typehint, is_attrs
