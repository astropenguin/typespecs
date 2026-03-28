__all__ = [
    # submodules
    "api",
    "dataframe",
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
__version__ = "3.0.0rc1"


# dependencies
from . import api, dataframe, typing
from .api import *
