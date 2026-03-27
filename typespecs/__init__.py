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
    "is_spec",
    "is_specframe",
]
__version__ = "2.0.2"


# dependencies
from . import api, dataframe, typing
from .api import *
