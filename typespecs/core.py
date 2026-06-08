__all__ = [
    "ITSELF",
    "Config",
    "ItselfType",
    "Spec",
    "from_annotated",
    "from_annotation",
    "from_annotations",
]

# standard library
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from itertools import repeat
from typing import TYPE_CHECKING, Annotated, Any, overload

# dependencies
import pandas as pd
from readonlydict import ReadonlyDict, Tuples
from typing_extensions import NotRequired, Self, TypedDict
from .frame import Resolution, collapse, concat, fillna, no_silent_downcasting
from .typing import get_annotation, get_annotations, get_metadata, get_subannotations


class Config(TypedDict):
    """Configuration for typespecs.

    This dictionary defines the configuration settings that can be provided
    via the ``__typespecs_config__`` attribute of an object to take precedence
    over the default behavior of ``typespecs.from_annotated``.
    """

    conflict: NotRequired[Mapping[str, Resolution] | Resolution]
    """Resolution strategy for conflicts between metadata.
    Either a single resolution or a mapping of column names
    to resolutions is accepted. As built-in resolutions,
    ``"override"`` (new value overrides old value; default behavior)
    and ``"update"`` (new mapping updates old mapping) are supported.
    A function that takes old and new values and returns
    resolved value can also be accepted as a custom resolution.
    """

    data: NotRequired[str | None]
    """Name of the column for the actual data of the annotations.
    If it is ``None``, the data column will not be created.
    """

    default: NotRequired[Mapping[str, Any] | Any]
    """Default value for each column. Either a single value
    or a mapping of column names to values is accepted.
    If the specified columns are not present in the created specification
    DataFrame, each column filled with the specified value will be added.
    """

    depth: NotRequired[int | None]
    """Maximum depth of sub-annotations to search.
    If it is ``None``, all sub-annotations will be searched.
    """

    merge: NotRequired[bool]
    """Whether to merge all sub-annotations into a single row.
    If it is ``False``, each sub-annotation will have its own row.
    """

    separator: NotRequired[str]
    """Separator for concatenating root and sub-indices."""

    type: NotRequired[str | None]
    """Name of the column for the metadata-stripped annotations.
    If it is ``None``, the type column will not be created.
    """


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
    conflict: Mapping[str, Resolution] | Resolution = "override",
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
        conflict: Resolution strategy for conflicts between metadata.
            Either a single resolution or a mapping of column names
            to resolutions is accepted. As built-in resolutions,
            ``"override"`` (new value overrides old value; default behavior)
            and ``"update"`` (new mapping updates old mapping) are supported.
            A function that takes old and new values and returns
            resolved value can also be accepted as a custom resolution.
        data: Name of the column for the actual data of the annotations.
            If it is ``None``, the data column will not be created.
        default: Default value for each column. Either a single value
            or a mapping of column names to values is accepted.
            If the specified columns are not present in the created specification
            DataFrame, each column filled with the specified value will be added.
        depth: Maximum depth of sub-annotations to search.
            If it is ``None``, all sub-annotations will be searched.
        merge: Whether to merge all sub-annotations into a single row.
            If it is ``False``, each sub-annotation will have its own row.
        separator: Separator for concatenating root and sub-indices.
        type: Name of the column for the metadata-stripped annotations.
            If it is ``None``, the type column will not be created.

    Returns:
        Created specification DataFrame.

    Note:
        If the given object has a ``__typespecs_config__`` attribute,
        the configuration settings defined in it will take precedence
        over the arguments passed to this function.
    """
    config = getattr(obj, "__typespecs_config__", {})
    conflict = config.get("conflict", conflict)
    data = config.get("data", data)
    default = config.get("default", default)
    depth = config.get("depth", depth)
    merge = config.get("merge", merge)
    separator = config.get("separator", separator)
    type = config.get("type", type)

    if data is None:
        annotations = get_annotations(obj)
    else:
        annotations: dict[str, Any] = {}

        for index, annotation in get_annotations(obj).items():
            spec = Spec({data: getattr(obj, index, pd.NA)})
            annotations[index] = Annotated[annotation, spec]

    annotations.pop("__typespecs_config__", None)

    return from_annotations(
        annotations,
        conflict=conflict,
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
    conflict: Mapping[str, Resolution] | Resolution = "override",
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
        conflict: Resolution strategy for conflicts between metadata.
            Either a single resolution or a mapping of column names
            to resolutions is accepted. As built-in resolutions,
            ``"override"`` (new value overrides old value; default behavior)
            and ``"update"`` (new mapping updates old mapping) are supported.
            A function that takes old and new values and returns
            resolved value can also be accepted as a custom resolution.
        default: Default value for each column. Either a single value
            or a mapping of column names to values is accepted.
            If the specified columns are not present in the created specification
            DataFrame, each column filled with the specified value will be added.
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
    with no_silent_downcasting():
        if obj is Ellipsis:
            # workaround for Python 3.10 and 3.11
            return new(None if type is None else {type: Ellipsis}, index)

        annotation = get_annotation(obj, recursive=True)

        if type is not None:
            obj = Annotated[obj, Spec({type: ITSELF})]

        specs = [
            {key: annotation if val == ITSELF else val for key, val in spec.items()}
            for spec in get_metadata(obj, type=Spec)
        ]

        if specs:
            root = collapse(concat(map(new, specs, repeat(index))), conflict)
        else:
            root = new(None, index)

        if depth == 0:
            return fillna(root, default)

        sub: list[pd.DataFrame] = []

        for subindex, subannotation in enumerate(get_subannotations(obj)):
            sub.append(
                from_annotation(
                    subannotation,
                    conflict=conflict,
                    default=pd.NA,
                    depth=None if depth is None else depth - 1,
                    index=f"{index}{separator}{subindex}",
                    merge=False,
                    separator=separator,
                    type=type,
                ),
            )

        if merge:
            return fillna(collapse(concat([*sub, root]), conflict), default)
        else:
            return fillna(concat([root, *sub]), default)


def from_annotations(
    obj: Mapping[str, Any],
    /,
    *,
    conflict: Mapping[str, Resolution] | Resolution = "override",
    default: Mapping[str, Any] | Any = pd.NA,
    depth: int | None = None,
    merge: bool = True,
    separator: str = "/",
    type: str | None = "type",
) -> pd.DataFrame:
    """Create a specification DataFrame from given annotations.

    Args:
        obj: The annotations to convert.
        conflict: Resolution strategy for conflicts between metadata.
            Either a single resolution or a mapping of column names
            to resolutions is accepted. As built-in resolutions,
            ``"override"`` (new value overrides old value; default behavior)
            and ``"update"`` (new mapping updates old mapping) are supported.
            A function that takes old and new values and returns
            resolved value can also be accepted as a custom resolution.
        default: Default value for each column. Either a single value
            or a mapping of column names to values is accepted.
            If the specified columns are not present in the created specification
            DataFrame, each column filled with the specified value will be added.
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
    with no_silent_downcasting():
        frames: list[pd.DataFrame] = []

        for index, annotation in obj.items():
            frames.append(
                from_annotation(
                    annotation,
                    conflict=conflict,
                    default=pd.NA,
                    depth=depth,
                    index=index,
                    merge=merge,
                    separator=separator,
                    type=type,
                )
            )

        if frames:
            return fillna(concat(frames), default)
        else:
            return new(None, None)


def new(
    data: Mapping[str, Any] | None = None,
    index: Iterable[str] | None = None,
    /,
) -> pd.DataFrame:
    """Create a new single-row specification DataFrame."""
    if data is None:
        return pd.DataFrame(
            None,
            None if index is None else [index],
            pd.Index([], dtype=str),
            dtype=object,
        )
    else:
        return pd.DataFrame(
            [data],
            None if index is None else [index],
            dtype=object,
        )
