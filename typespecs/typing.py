__all__ = [
    "DataClass",
    "gen_subtypes",
    "get_annotated",
    "get_annotations",
    "is_annotated",
    "is_literal",
]


# standard library
from collections.abc import Iterator
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


def gen_subtypes(obj: Any, /) -> Iterator[Any]:
    """Generate subtypes if given object is a generic type.

    Args:
        obj: The object to inspect.

    Yields:
        The subtypes of the object.

    """
    if is_literal(annotated := get_annotated(obj)):
        yield
    else:
        yield from get_args(annotated)


def get_annotated(obj: Any, /, *, recursive: bool = False) -> Any:
    """Return the bare type if given object is an annotated type.

    Args:
        obj: The object to inspect.
        recursive: Whether to recursively strip all annotations.

    Returns:
        The bare type of the object.

    """
    if recursive:
        return _strip_annotations(obj)  # type: ignore
    else:
        return get_args(obj)[0] if is_annotated(obj) else obj


def get_annotations(obj: Any, /) -> list[Any]:
    """Get all type annotations of given object.

    Args:
        obj: The object to inspect.

    Returns:
        List of all type annotations of the object.

    """
    return [*get_args(obj)[1:]] if is_annotated(obj) else []


def is_annotated(obj: Any, /) -> bool:
    """Check if given object is an annotated type.

    Args:
        obj: The object to inspect.

    Returns:
        True if the object is an annotated type. False otherwise.

    """
    return get_origin(obj) is Annotated


def is_literal(obj: Any, /) -> bool:
    """Check if given object is a literal type.

    Args:
        obj: The object to inspect.

    Returns:
        True if the object is a literal type. False otherwise.

    """
    return get_origin(obj) is Literal
