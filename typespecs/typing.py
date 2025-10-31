__all__ = [
    "gen_subtypes",
    "get_annotated",
    "is_annotated",
    "is_literal",
    "is_union",
]


# standard library
import types
from collections.abc import Iterator
from typing import Annotated, Any, Literal, Union
from typing import _strip_annotations  # type: ignore


# dependencies
from typing_extensions import get_args, get_origin


def gen_subtypes(obj: Any, /) -> Iterator[Any]:
    """Generate subtypes if given object is a generic type.

    Args:
        obj: The object to inspect.

    Yields:
        The subtypes of the given object.

    """
    if is_annotated(obj):
        yield from gen_subtypes(get_args(obj)[0])
    elif is_union(obj):
        for arg in get_args(obj):
            yield from gen_subtypes(arg)
    elif not is_literal(obj):
        yield from get_args(obj)


def get_annotated(obj: Any, /) -> Any:
    """Return the bare type if given object is an annotated type.

    Args:
        obj: The object to inspect.

    Returns:
        The bare type of the given object.

    """
    return _strip_annotations(obj)  # type: ignore


def is_annotated(obj: Any, /) -> bool:
    """Check if given object is an annotated type.

    Args:
        obj: The object to inspect.

    Returns:
        True if the given object is an annotated type. False otherwise.

    """
    return get_origin(obj) is Annotated


def is_literal(obj: Any, /) -> bool:
    """Check if given object is a literal type.

    Args:
        obj: The object to inspect.

    Returns:
        True if the given object is a literal type. False otherwise.

    """
    return get_origin(obj) is Literal


def is_union(obj: Any, /) -> bool:
    """Check if given object is a union type.

    Args:
        obj: The object to inspect.

    Returns:
        True if the given object is a union type. False otherwise.

    """
    if (UnionType := getattr(types, "UnionType", None)) is not None:
        # For Python >= 3.10
        return get_origin(obj) is Union or isinstance(obj, UnionType)
    else:
        # For Python < 3.10
        return get_origin(obj) is Union
