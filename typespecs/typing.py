__all__ = [
    "DataClass",
    "get_annotation",
    "get_metadata",
    "get_subtypes",
    "has_metadata",
    "is_literal",
]


# standard library
from dataclasses import Field
from typing import Annotated, Any, ClassVar, Literal, Protocol
from typing import _strip_annotations  # type: ignore


# dependencies
from typing_extensions import get_args, get_origin


# type hints
class DataClassInstance(Protocol):
    """Type hint for any data-class instance."""

    __dataclass_fields__: ClassVar[dict[str, Field[Any]]]


DataClass = DataClassInstance | type[DataClassInstance]
"""Type hint for any data class or data-class instance."""


def get_annotation(obj: Any, /, *, recursive: bool = False) -> Any:
    """Return metadata-stripped annotation of given object.

    Args:
        obj: Object to inspect.
        recursive: Whether to recursively strip all metadata.

    Returns:
        Metadata-stripped annotation of the object.

    """
    if recursive:
        return _strip_annotations(obj)  # type: ignore
    else:
        return get_args(obj)[0] if has_metadata(obj) else obj


def get_metadata(obj: Any, /) -> list[Any]:
    """Return all metadata of given object.

    Args:
        obj: Object to inspect.

    Returns:
        List of all metadata of the object.

    """
    return [*get_args(obj)[1:]] if has_metadata(obj) else []


def get_subtypes(obj: Any, /) -> list[Any]:
    """Return all subtypes of given object.

    Args:
        obj: Object to inspect.

    Returns:
        List of all subtypes of the object.

    """
    if is_literal(annotation := get_annotation(obj)):
        return []
    else:
        return list(get_args(annotation))


def has_metadata(obj: Any, /) -> bool:
    """Check if given object has metadata.

    Args:
        obj: Object to inspect.

    Returns:
        True if the object has metadata. False otherwise.

    """
    return get_origin(obj) is Annotated


def is_literal(obj: Any, /) -> bool:
    """Check if given object is a literal type.

    Args:
        obj: Object to inspect.

    Returns:
        True if the object is a literal type. False otherwise.

    """
    return get_origin(obj) is Literal
