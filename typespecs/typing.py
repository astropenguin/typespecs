__all__ = [
    "del_metadata",
    "get_annotation",
    "get_annotations",
    "get_metadata",
    "get_subannotations",
    "has_metadata",
    "is_literal",
]

# standard library
from typing import Annotated, Any, Literal, TypeVar, overload
from typing import _strip_annotations  # type: ignore
from warnings import warn

# dependencies
from typing_extensions import (
    get_annotations as _get_annotations,
    get_args,
    get_origin,
)

# type hints
T = TypeVar("T")


def del_metadata(annotation: Any, /, *, recursive: bool = False) -> Any:
    """Return metadata-stripped annotation.

    Args:
        annotation: Annotation to strip metadata from.
        recursive: Whether to recursively strip metadata of sub-annotations.

    Returns:
        Metadata-stripped annotation.
    """
    if recursive:
        return _strip_annotations(annotation)  # type: ignore
    elif has_metadata(annotation):
        return get_args(annotation)[0]
    else:
        return annotation


def get_annotation(annotation: Any, /, *, recursive: bool = False) -> Any:
    """Return metadata-stripped annotation.

    Args:
        annotation: Annotation to strip metadata from.
        recursive: Whether to recursively strip metadata of sub-annotations.

    Returns:
        Metadata-stripped annotation.
    """
    warn(
        "This function will be deprecated in the next major version."
        "Use ``del_metadata(annotation, recursive=recursive)`` instead.",
        DeprecationWarning,
    )
    return del_metadata(annotation, recursive=recursive)


def get_annotations(cls_or_obj: Any, /) -> dict[str, Any]:
    """Return annotations of given class or object.

    If it is a class instance, this function tries to retrieve
    the annotations from its class rather than the instance itself.

    Args:
        cls_or_obj: Class or object to inspect.

    Returns:
        Dictionary of annotations of the class or object.
    """
    if isinstance(cls_or_obj, type):
        return _get_annotations(cls_or_obj)
    else:
        return _get_annotations(type(cls_or_obj))


@overload
def get_metadata(annotation: Any, /, *, type: None = None) -> list[Any]: ...
@overload
def get_metadata(annotation: Any, /, *, type: type[T]) -> list[T]: ...
def get_metadata(annotation: Any, /, *, type: Any = None) -> Any:
    """Return metadata of given annotation.

    Args:
        annotation: Annotation to inspect.
        type: Type of metadata to filter. If specified,
            only metadata of the given type will be returned.
            Otherwise, all metadata will be returned.

    Returns:
        List of metadata of the annotation.
    """
    metadata = get_args(annotation)[1:] if has_metadata(annotation) else ()

    if type is None:
        return list(metadata)
    else:
        return [item for item in metadata if isinstance(item, type)]


def get_subannotations(annotation: Any, /) -> list[Any]:
    """Return sub-annotations of given annotation.

    Args:
        annotation: Annotation to inspect.

    Returns:
        List of sub-annotations of the annotation.
    """
    if is_literal(annotation := del_metadata(annotation)):
        return []
    else:
        return list(get_args(annotation))


def has_metadata(annotation: Any, /) -> bool:
    """Check if given annotation has metadata.

    Args:
        annotation: Annotation to inspect.

    Returns:
        ``True`` if the annotation has metadata. ``False`` otherwise.
    """
    return get_origin(annotation) is Annotated


def is_literal(annotation: Any, /) -> bool:
    """Check if given annotation is a literal type.

    Args:
        annotation: Annotation to inspect.

    Returns:
        ``True`` if the annotation is a literal type. ``False`` otherwise.
    """
    return get_origin(annotation) is Literal
