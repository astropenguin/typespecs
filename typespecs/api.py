__all__ = ["from_annotated", "from_annotation", "from_annotations"]


# standard library
from collections.abc import Iterable
from typing import Annotated, Any, cast


# dependencies
import pandas as pd
from .spec import ITSELF, Spec, SpecFrame, is_spec
from .typing import get_annotation, get_annotations, get_metadata, get_subannotations


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
    if type is not None:
        obj = Annotated[obj, Spec({type: ITSELF})]

    specs: dict[str, Any] = {}
    type_ = get_annotation(obj, recursive=True)

    for spec in filter(is_spec, get_metadata(obj)):
        specs.update(spec.replace(ITSELF, type_))

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

    with pd.option_context("future.no_silent_downcasting", True):
        return SpecFrame(_default(_concat(frames), default))


def _concat(objs: Iterable[pd.DataFrame], /) -> pd.DataFrame:
    """Concatenate DataFrames with missing values filled with <NA>.

    Args:
        objs: DataFrames to concatenate.

    Returns:
        Concatenated DataFrame.

    """
    indexes = [obj.index for obj in objs]
    columns = [obj.columns for obj in objs]
    frame = pd.DataFrame(
        data=pd.NA,
        index=pd.Index([]).append(indexes),
        columns=pd.Index([]).append(columns).unique().sort_values(),
        dtype=object,
    )

    for obj in objs:
        frame.loc[obj.index, obj.columns] = obj

    return frame


def _default(obj: pd.DataFrame, value: dict[str, Any] | Any, /) -> pd.DataFrame:
    """Fill missing values in given DataFrame with given value.

    Args:
        obj: DataFrame to fill.
        value: Default value for each column. Either a single value
            or a dictionary mapping column names to values is accepted.

    Returns:
        DataFrame with missing values filled.

    """
    if isinstance(value, dict):
        values = cast(dict[str, Any], value)
    else:
        values = {key: value for key in obj.columns}

    missings = {key: pd.NA for key in set(values) - set(obj.columns)}
    replaces = {key: {pd.NA: val} for key, val in values.items()}
    return obj.assign(**missings).replace(replaces)


def _isna(obj: Any, /) -> bool:
    """Check if given object is identical to <NA>.

    Args:
        obj: Object to inspect.

    Returns:
        True if the object is <NA>. False otherwise.

    """
    return obj is pd.NA


def _merge(obj: pd.DataFrame, /) -> pd.DataFrame:
    """Merge multiple rows of a DataFrame into a single row.

    Args:
        obj: DataFrame to merge.

    Returns:
        Merged DataFrame.

    """
    try:
        # for pandas >= 2.1
        isna = obj.map(_isna)
    except AttributeError:
        # for pandas < 2.1
        isna = obj.applymap(_isna)  # type: ignore

    return obj.mask(isna, obj.bfill()).head(1)  # type: ignore
