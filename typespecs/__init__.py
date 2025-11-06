__all__ = [
    "Attrs",
    "Spec",
    "api",
    "from_dataclass",
    "from_typehint",
    "is_attrs",
    "is_spec",
    "spec",
    "typing",
]
__version__ = "0.2.0"


# dependencies
from . import api
from . import spec
from . import typing
from .api import Attrs, from_dataclass, from_typehint, is_attrs
from .spec import Spec, is_spec
