__all__ = [
    "DataClass",
    "get_annotated",
    "get_annotations",
    "get_subtypes",
    "is_annotated",
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


def get_annotated(obj: Any, /, *, recursive: bool = False) -> Any:
    """Return the bare type if given object is an annotated type.

    Args:
        obj: Object to inspect.
        recursive: Whether to recursively strip all annotations.

    Returns:
        Bare type of the object.

    """
    if recursive:
        return _strip_annotations(obj)  # type: ignore
    else:
        return get_args(obj)[0] if is_annotated(obj) else obj


def get_annotations(obj: Any, /) -> list[Any]:
    """Return all type annotations of given object.

    Args:
        obj: Object to inspect.

    Returns:
        List of all type annotations of the object.

    """
    return [*get_args(obj)[1:]] if is_annotated(obj) else []


def get_subtypes(obj: Any, /) -> list[Any]:
    """Return all subtypes of given object.

    Args:
        obj: Object to inspect.

    Returns:
        List of all subtypes of the object.

    """
    if is_literal(annotated := get_annotated(obj)):
        return []
    else:
        return list(get_args(annotated))


def is_annotated(obj: Any, /) -> bool:
    """Check if given object is an annotated type.

    Args:
        obj: Object to inspect.

    Returns:
        True if the object is an annotated type. False otherwise.

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
