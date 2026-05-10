__all__ = [
    "ITSELF",
    "ItselfType",
    "Spec",
    "from_annotated",
    "from_annotation",
    "from_annotations",
]

# standard library
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import TYPE_CHECKING, Annotated, Any, overload

# dependencies
import pandas as pd
from packaging.version import Version
from pandas import __version__ as PANDAS_VERSION
from readonlydict import ReadonlyDict, Tuples
from typing_extensions import Self
from .frame import concat, default as default_, merge as merge_
from .typing import get_annotation, get_annotations, get_metadata, get_subannotations


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

        @overload
        def __new__(cls, **kwargs: Any) -> Self: ...
        @overload
        def __new__(cls, mapping: Mapping[str, Any], /, **kwargs: Any) -> Self: ...
        @overload
        def __new__(cls, iterable: Tuples[str, Any], /, **kwargs: Any) -> Self: ...

        @overload
        @classmethod
        def fromkeys(cls, iterable: Iterable[str], /) -> Self: ...
        @overload
        @classmethod
        def fromkeys(cls, iterable: Iterable[str], value: Any, /) -> Self: ...

        def __or__(self, other: Mapping[str, Any], /) -> Self: ...


def from_annotated(
    obj: Any,
    /,
    data: str | None = "data",
    default: Mapping[str, Any] | Any = pd.NA,
    depth: int | None = None,
    merge: bool = True,
    separator: str = "/",
    type: str | None = "type",
) -> pd.DataFrame:
    """Create a specification DataFrame from given object with annotations.

    Args:
        obj: The object to convert.
        data: Name of the column for the actual data of the annotations.
            If it is ``None``, the data column will not be created.
        depth: Maximum depth of sub-annotations to search.
            If it is ``None``, all sub-annotations will be searched.
        default: Default value for each column. Either a single value
            or a mapping of column names to values is accepted.
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
        depth=depth,
        merge=merge,
        separator=separator,
        type=type,
    )


def from_annotation(
    obj: Any,
    /,
    *,
    default: Mapping[str, Any] | Any = pd.NA,
    depth: int | None = None,
    index: str = "root",
    merge: bool = True,
    separator: str = "/",
    type: str | None = "type",
) -> pd.DataFrame:
    """Create a specification DataFrame from given annotation.

    Args:
        obj: The annotation to convert.
        default: Default value for each column. Either a single value
            or a mapping of column names to values is accepted.
        depth: Maximum depth of sub-annotations to search.
            If it is ``None``, all sub-annotations will be searched.
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

    itself = get_annotation(obj, recursive=True)
    specs: dict[str, Any] = {}

    for meta in get_metadata(obj):
        if isinstance(meta, Spec):
            for key, value in meta.items():
                specs[key] = itself if value == ITSELF else value

    frames = [
        pd.DataFrame(
            data={key: [value] for key, value in specs.items()},
            index=[index],
            dtype=object,
        )
    ]

    if depth is None or depth > 0:
        for subindex, subannotation in enumerate(get_subannotations(obj)):
            frames.append(
                from_annotation(
                    subannotation,
                    default=pd.NA,
                    depth=None if depth is None else depth - 1,
                    index=f"{index}{separator}{subindex}",
                    merge=False,
                    separator=separator,
                    type=type,
                )
            )

    if Version(PANDAS_VERSION) >= Version("3"):
        if merge:
            return default_(merge_(concat(frames)), default)
        else:
            return default_(concat(frames), default)

    with pd.option_context("future.no_silent_downcasting", True):
        if merge:
            return default_(merge_(concat(frames)), default)
        else:
            return default_(concat(frames), default)


def from_annotations(
    obj: Mapping[str, Any],
    /,
    *,
    default: Mapping[str, Any] | Any = pd.NA,
    depth: int | None = None,
    merge: bool = True,
    separator: str = "/",
    type: str | None = "type",
) -> pd.DataFrame:
    """Create a specification DataFrame from given annotations.

    Args:
        obj: The annotations to convert.
        default: Default value for each column. Either a single value
            or a mapping of column names to values is accepted.
        depth: Maximum depth of sub-annotations to search.
            If it is ``None``, all sub-annotations will be searched.
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
                depth=depth,
                index=index,
                merge=merge,
                separator=separator,
                type=type,
            )
        )

    if Version(PANDAS_VERSION) >= Version("3"):
        return default_(concat(frames), default)

    with pd.option_context("future.no_silent_downcasting", True):
        return default_(concat(frames), default)


def from_ellipsis(
    *,
    index: str = "root",
    type: str | None = "type",
) -> pd.DataFrame:
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
        return pd.DataFrame(index=[index], dtype=object)
    else:
        return pd.DataFrame(data={type: ...}, index=[index], dtype=object)
