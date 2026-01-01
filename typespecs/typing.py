__all__ = [
    "get_annotation",
    "get_annotations",
    "get_metadata",
    "get_subannotations",
    "has_metadata",
    "is_literal",
]


# standard library
from typing import Annotated, Any, Literal
from typing import _strip_annotations  # type: ignore


# dependencies
from typing_extensions import get_args, get_origin
from typing_extensions import get_annotations as _get_annotations


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


def get_annotations(obj: Any, /) -> dict[str, Any]:
    """Return all annotations of given object.

    Prior to Python 3.14, this is identical to
    ``typing_extensions.get_annotations``.
    For Python 3.14 and later, it falls back to
    the object's class if ``__annotations__`` is missing.

    Args:
        obj: Object to inspect.

    Returns:
        Dictionary of all annotations of the object.

    """
    if hasattr(obj, "__annotations__"):
        return _get_annotations(obj)
    else:
        return _get_annotations(type(obj))


def get_metadata(obj: Any, /) -> list[Any]:
    """Return all metadata of given object.

    Args:
        obj: Object to inspect.

    Returns:
        List of all metadata of the object.

    """
    return list(get_args(obj)[1:]) if has_metadata(obj) else []


def get_subannotations(obj: Any, /) -> list[Any]:
    """Return all sub-annotations of given object.

    Args:
        obj: Object to inspect.

    Returns:
        List of all sub-annotations of the object.

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
