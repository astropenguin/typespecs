__all__ = [
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

# standard library
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import TYPE_CHECKING, Annotated, Any, overload

# dependencies
import pandas as pd
from packaging.version import Version
from readonlydict import ReadonlyDict
from typing_extensions import Self, TypeGuard
from .typing import (
    get_annotation,
    get_annotations,
    get_metadata,
    get_subannotations,
)
from .utils import (
    concat as _concat,
    default as _default,
    merge as _merge,
    replace as _replace,
)


@dataclass(frozen=True)
class ItselfType:
    """Sentinel object specifying metadata-stripped annotation itself."""

    __array_ufunc__ = None

    def __repr__(self) -> str:
        return "<ITSELF>"


ITSELF = ItselfType()
"""Sentinel object specifying metadata-stripped annotation itself."""


class Spec(ReadonlyDict[str, Any]):
    """Type specification.

    This is a subclass of the read-only dictionary without any runtime modifications.
    It is intended to distinguish a type specification from other type metadata.

    """

    if TYPE_CHECKING:
        # fmt: off
        @overload
        def __new__(cls, **kwargs: Any) -> Self:...
        @overload
        def __new__(cls, mapping: Mapping[str, Any], /, **kwargs: Any) -> Self: ...
        @overload
        def __new__(cls, iterable: Iterable[tuple[str, Any]], /, **kwargs: Any) -> Self: ...
        # fmt: on

        @overload
        @classmethod
        def fromkeys(cls, iterable: Iterable[str], /) -> Self: ...
        @overload
        @classmethod
        def fromkeys(cls, iterable: Iterable[str], value: Any, /) -> Self: ...

        def __or__(self, other: Mapping[str, Any], /) -> Self: ...


class SpecFrame(pd.DataFrame):
    """Specification DataFrame.

    This is a subclass of the pandas DataFrame without any runtime modifications.
    It is intended to distinguish a specification DataFrame from other DataFrames.

    """


def from_annotated(
    obj: Any,
    /,
    data: str | None = "data",
    default: dict[str, Any] | Any = pd.NA,
    merge: bool = True,
    separator: str = "/",
    type: str | None = "type",
) -> SpecFrame:
    """Create a specification DataFrame from given object with annotations.

    Args:
        obj: The object to convert.
        data: Name of the column for the actual data of the annotations.
            If it is ``None``, the data column will not be created.
        default: Default value for each column. Either a single value
            or a dictionary mapping column names to values is accepted.
        merge: Whether to merge all sub-annotations into a single row.
            If it is ``False``, each sub-annotation will have its own row.
        separator: Separator for concatenating root and sub-indices.
        type: Name of the column for the metadata-stripped annotations.
            If it is ``None``, the type column will not be created.

    Returns:
        Created specification DataFrame.

    """
    if data is None:
        annotations = get_annotations(obj)
    else:
        annotations: dict[str, Any] = {}

        for index, annotation in get_annotations(obj).items():
            spec = Spec({data: getattr(obj, index, pd.NA)})
            annotations[index] = Annotated[annotation, spec]

    return from_annotations(
        annotations,
        default=default,
        merge=merge,
        separator=separator,
        type=type,
    )


def from_annotation(
    obj: Any,
    /,
    *,
    default: dict[str, Any] | Any = pd.NA,
    index: str = "root",
    merge: bool = True,
    separator: str = "/",
    type: str | None = "type",
) -> SpecFrame:
    """Create a specification DataFrame from given annotation.

    Args:
        obj: The annotation to convert.
        default: Default value for each column. Either a single value
            or a dictionary mapping column names to values is accepted.
        index: Root index of the created specification DataFrame.
        merge: Whether to merge all sub-annotations into a single row.
            If it is ``False``, each sub-annotation will have its own row.
        separator: Separator for concatenating root and sub-indices.
        type: Name of the column for the metadata-stripped annotations.
            If it is ``None``, the type column will not be created.

    Returns:
        Created specification DataFrame.

    """
    if obj is Ellipsis:
        return from_ellipsis(index=index, type=type)

    if type is not None:
        obj = Annotated[obj, Spec({type: ITSELF})]

    specs: dict[str, Any] = {}
    itself = get_annotation(obj, recursive=True)

    for spec in filter(is_spec, get_metadata(obj)):
        specs.update(_replace(spec, ITSELF, itself))

    frames = [
        pd.DataFrame(
            data={key: [value] for key, value in specs.items()},
            index=[index],
            dtype=object,
        )
    ]

    for subindex, subannotation in enumerate(get_subannotations(obj)):
        frames.append(
            from_annotation(
                subannotation,
                index=f"{index}{separator}{subindex}",
                merge=False,
                separator=separator,
                type=type,
            )
        )

    if Version(pd.__version__) >= Version("3"):
        if merge:
            return SpecFrame(_default(_merge(_concat(frames)), default))
        else:
            return SpecFrame(_default(_concat(frames), default))

    with pd.option_context("future.no_silent_downcasting", True):
        if merge:
            return SpecFrame(_default(_merge(_concat(frames)), default))
        else:
            return SpecFrame(_default(_concat(frames), default))


def from_annotations(
    obj: dict[str, Any],
    /,
    *,
    default: dict[str, Any] | Any = pd.NA,
    merge: bool = True,
    separator: str = "/",
    type: str | None = "type",
) -> SpecFrame:
    """Create a specification DataFrame from given annotations.

    Args:
        obj: The annotations to convert.
        default: Default value for each column. Either a single value
            or a dictionary mapping column names to values is accepted.
        merge: Whether to merge all sub-annotations into a single row.
            If it is ``False``, each sub-annotation will have its own row.
        separator: Separator for concatenating root and sub-indices.
        type: Name of the column for the metadata-stripped annotations.
            If it is ``None``, the type column will not be created.

    Returns:
        Created specification DataFrame.

    """
    frames: list[pd.DataFrame] = []

    for index, annotation in obj.items():
        frames.append(
            from_annotation(
                annotation,
                default=pd.NA,
                index=index,
                merge=merge,
                separator=separator,
                type=type,
            )
        )

    if Version(pd.__version__) >= Version("3"):
        return SpecFrame(_default(_concat(frames), default))

    with pd.option_context("future.no_silent_downcasting", True):
        return SpecFrame(_default(_concat(frames), default))


def from_ellipsis(
    *,
    index: str = "root",
    type: str | None = "type",
) -> SpecFrame:
    """Create a specification DataFrame from an Ellipsis.

    Args:
        index: Root index of the created specification DataFrame.
        type: Name of the column for the metadata-stripped annotations.
            If it is ``None``, the type column will not be created.

    Returns:
        Created specification DataFrame.

    Note:
        This function is only for supporting Python 3.10 and 3.11
        where ``Annotated[Ellipsis, ...]`` does not work properly.
        It will be removed if they are no longer supported in the package.

    """
    if type is None:
        return SpecFrame(index=[index], dtype=object)
    else:
        return SpecFrame(data={type: ...}, index=[index], dtype=object)


def is_spec(obj: Any, /) -> TypeGuard[Spec]:
    """Check if given object is a type specification.

    Args:
        obj: Object to inspect.

    Returns:
        True if the object is a type specification. False otherwise.

    """
    return isinstance(obj, Spec)


def is_specframe(obj: Any, /) -> TypeGuard[SpecFrame]:
    """Check if given object is a specification DataFrame.

    Args:
        obj: Object to inspect.

    Returns:
        True if the object is a specification DataFrame. False otherwise.

    """
    return isinstance(obj, SpecFrame)
