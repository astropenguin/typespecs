__all__ = [
    "Config",
    "Consts",
    "Spec",
    "from_annotated",
    "from_annotation",
    "from_annotations",
]

# standard library
from collections.abc import Hashable, Iterable, Iterator, Mapping
from enum import Enum, auto
from typing import TYPE_CHECKING, Annotated, Any, TypeVar, overload

# dependencies
import pandas as pd
from readonlydict import Items, ReadonlyDict
from typing_extensions import NotRequired, Self, TypedDict
from .mapping import (
    Multiple,
    Resolver,
    fill,
    group as group_,
    merge as merge_,
    pop,
    sort,
)
from .typing import (
    del_metadata,
    get_annotations,
    get_metadata,
    get_subannotations,
)


# constants
class Consts(Enum):
    """Constants for typespecs."""

    INDICES = auto()
    """Key for the indices of a type specification (internal use)."""

    ITSELF = auto()
    """Sentinel for specifying metadata-stripped annotation itself."""

    def __repr__(self) -> str:
        return f"<{self.name}>"


# type hints
TKey = TypeVar("TKey", bound=Hashable)


class Config(TypedDict):
    """Configuration for typespecs.

    This dictionary defines the configuration settings that can be provided
    via the ``__typespecs_config__`` attribute of an object to take precedence
    over the default behavior of ``typespecs.from_annotated``.
    """

    conflict: NotRequired[Multiple[Resolver]]
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

    default: NotRequired[Multiple[Any]]
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


class Spec(ReadonlyDict[Hashable, Any]):
    """Type specification.

    This is a subclass of the read-only dictionary without any runtime modifications.
    It is intended to distinguish a type specification from other type metadata.
    """

    if TYPE_CHECKING:

        @overload
        def __new__(cls, iterable: Items[TKey, Any], /, **kwargs: Any) -> Self: ...
        @overload
        def __new__(cls, mapping: Mapping[TKey, Any], /, **kwargs: Any) -> Self: ...
        @overload
        def __new__(cls, **kwargs: Any) -> Self: ...
        def __new__(cls, *args: Any, **kwargs: Any) -> Any: ...

        @overload
        @classmethod
        def fromkeys(cls, iterable: Iterable[TKey], /) -> Self: ...
        @overload
        @classmethod
        def fromkeys(cls, iterable: Iterable[TKey], value: Any, /) -> Self: ...
        @classmethod
        def fromkeys(cls, *args: Any, **kwargs: Any) -> Any: ...

        def __or__(self, other: Mapping[TKey, Any], /) -> Self: ...


def from_annotated(
    obj: Any,
    /,
    conflict: Multiple[Resolver] = "override",
    data: str | None = "data",
    default: Multiple[Any] = pd.NA,
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
    conflict: Multiple[Resolver] = "override",
    default: Multiple[Any] = pd.NA,
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
    specs = pre(
        obj,
        conflict=conflict,
        depth=depth,
        index=index,
        merge=merge,
        type=type,
    )
    return post(specs, default=default, separator=separator)


def from_annotations(
    obj: Mapping[str, Any],
    /,
    *,
    conflict: Multiple[Resolver] = "override",
    default: Multiple[Any] = pd.NA,
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
    specs: list[dict[Hashable, Any]] = []

    for index, annotation in obj.items():
        specs.extend(
            pre(
                annotation,
                conflict=conflict,
                depth=depth,
                index=index,
                merge=merge,
                type=type,
            )
        )

    return post(specs, default=default, separator=separator)


def find(
    annotation: Any,
    /,
    *,
    depth: int | None = None,
    indices: tuple[Hashable, ...] = ("root",),
    type: str | None = "type",
) -> Iterator[dict[Hashable, Any]]:
    """Find all type specifications (with indices) in given annotation."""
    itself = del_metadata(annotation, recursive=True)

    if type is None:
        yield {Consts.INDICES: (*indices, float("inf"))}
    else:
        yield {Consts.INDICES: (*indices, float("inf")), type: itself}

    for order, spec in enumerate(get_metadata(annotation, type=Spec)):
        yield {
            Consts.INDICES: (*indices, float("inf"), order),
            **{
                key: itself if val is Consts.ITSELF else val
                for key, val in spec.items()
            },
        }

    if depth != 0:
        for order, subann in enumerate(get_subannotations(annotation)):
            yield from find(
                subann,
                depth=None if depth is None else depth - 1,
                indices=(*indices, order),
            )


def pre(
    annotation: Any,
    /,
    conflict: Multiple[Resolver] = "override",
    depth: int | None = None,
    index: str = "root",
    merge: bool = True,
    type: str | None = "type",
) -> list[dict[Hashable, Any]]:
    """Create a list of type specifications from given annotation."""

    def to_key(spec: dict[Hashable, Any], /) -> tuple[Hashable, ...]:
        return key_of(spec[Consts.INDICES])

    specs = sort(
        find(annotation, depth=depth, indices=(index,), type=type),
        Consts.INDICES,
    )

    if merge:
        return sort(
            [merge_(specs, conflict)],
            Consts.INDICES,
            reverse=True,
        )
    else:
        return sort(
            [merge_(group, conflict) for group in group_(specs, to_key)],
            Consts.INDICES,
            reverse=True,
        )


def post(
    specs: list[dict[Hashable, Any]],
    /,
    default: Multiple[Any] = pd.NA,
    separator: str = "/",
) -> pd.DataFrame:
    """Create a specification DataFrame from given type specifications."""

    def to_index(indices: tuple[Hashable, ...], /) -> str:
        return separator.join(map(str, key_of(indices)))

    index = list(map(to_index, pop(specs, Consts.INDICES)))

    return pd.DataFrame(
        data=fill(specs, default),
        index=index,
        dtype=object,
    ).sort_index(axis=1)


def key_of(indices: tuple[Hashable, ...], /) -> tuple[Hashable, ...]:
    """Return the subset of the given indices that is valid for a key."""
    return indices[: indices.index(float("inf"))]
