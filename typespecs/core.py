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
from typing import TYPE_CHECKING, Annotated, Any, overload

# dependencies
import pandas as pd
from readonlydict import Items, ReadonlyDict
from typing_extensions import NotRequired, Self, TypedDict
from .frame import Resolution, collapse, concat, fillna
from .typing import del_metadata, get_annotations, get_metadata, get_subannotations


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
        def __new__(cls, iterable: Items[str, Any], /, **kwargs: Any) -> Self: ...
        @overload
        def __new__(cls, mapping: Mapping[str, Any], /, **kwargs: Any) -> Self: ...

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
    parsed = parse_annotation(
        obj,
        depth=depth,
        index=index,
        separator=separator,
        type=type,
    )

    if merge:
        collapsed = collapse(parsed, conflict)
    else:
        collapsed = concat(
            collapse(frame, conflict)
            for _, frame in parsed.groupby(group_keys=False, level=0)
        )

    collapsed.index = collapsed.index.get_level_values(0)
    return fillna(collapsed, default)


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
        return pd.DataFrame(
            None,
            pd.Index([], dtype=str),
            pd.Index([], dtype=str),
            dtype=object,
        )


def parse_annotation(
    annotation: Any,
    /,
    *,
    depth: int | None = None,
    index: str = "root",
    separator: str = "/",
    type: str | None = "type",
) -> pd.DataFrame:
    """Parse type specifications in given annotation.

    Args:
        annotation: Annotation to inspect.
        depth: Maximum depth of sub-annotations to search.
            If it is ``None``, all sub-annotations will be searched.
        index: Root index of the created DataFrame.
        separator: Separator for concatenating root and sub-indices.
        type: Name of the column for the metadata-stripped annotations.
            If it is ``None``, the type column will not be created.

    Returns:
        DataFrame of the parsed type specifications.
    """
    if annotation is Ellipsis:
        return parse_spec({} if type is None else {type: Ellipsis}, index)

    if type is not None:
        annotation = Annotated[annotation, Spec({type: ITSELF})]

    bare = del_metadata(annotation, recursive=True)
    main: list[pd.DataFrame] = []
    subs: list[pd.DataFrame] = []

    for subindex, spec in enumerate(get_metadata(annotation, type=Spec)):
        main.append(
            parse_spec(
                {k: bare if v == ITSELF else v for k, v in spec.items()},
                index,
                subindex,
            )
        )

    if not main:
        main.append(parse_spec({}, index))

    if depth != 0:
        for subindex, subann in enumerate(get_subannotations(annotation)):
            subs.append(
                parse_annotation(
                    subann,
                    depth=None if depth is None else depth - 1,
                    index=f"{index}{separator}{subindex}",
                    separator=separator,
                    type=type,
                )
            )

    return concat([*subs, *main])


def parse_spec(
    spec: Mapping[str, Any],
    index: str,
    subindex: int = 0,
    /,
) -> pd.DataFrame:
    """Parse given type specification.

    Args:
        spec: Type specification to parse.
        index: Index of the created DataFrame.
        subindex: Sub-index of the created DataFrame.

    Returns:
        DataFrame of the parsed type specification.
    """
    return pd.DataFrame(
        data=[spec],
        index=pd.MultiIndex.from_arrays(
            [
                pd.Index([index], dtype=str),
                pd.Index([subindex], dtype=int),
            ]
        ),
        columns=pd.Index(spec, dtype=str),
        dtype=object,
    )
