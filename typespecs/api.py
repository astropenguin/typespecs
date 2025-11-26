__all__ = ["from_annotated", "from_annotation"]


# standard library
from collections.abc import Iterable
from typing import Annotated, Any


# dependencies
import pandas as pd
from .spec import ITSELF, Spec, is_spec
from .typing import (
    HasAnnotations,
    get_annotation,
    get_annotations,
    get_metadata,
    get_subannotations,
)


def from_annotated(
    obj: HasAnnotations,
    /,
    data: str | None = "data",
    merge: bool = True,
    separator: str = "/",
    type: str | None = "type",
) -> pd.DataFrame:
    """Create a specification DataFrame from given object with annotations.

    Args:
        obj: The object to convert.
        data: Name of the column for the actual data of the annotations.
        merge: Whether to merge all subtypes into a single row.
        separator: Separator for concatenating root and sub-indices.
        type: Name of the column for the metadata-stripped annotations.

    Returns:
        Created specification DataFrame.

    """
    frames: list[pd.DataFrame] = []

    for index, annotation in get_annotations(obj).items():
        if data is not None:
            data_ = getattr(obj, index, pd.NA)
            annotation = Annotated[annotation, Spec({data: data_})]

        frames.append(
            from_annotation(
                annotation,
                index=index,
                merge=merge,
                separator=separator,
                type=type,
            )
        )

    with pd.option_context("future.no_silent_downcasting", True):
        return _concat(frames)


def from_annotation(
    obj: Any,
    /,
    *,
    index: str = "root",
    merge: bool = True,
    separator: str = "/",
    type: str | None = "type",
) -> pd.DataFrame:
    """Create a specification DataFrame from given annotation.

    Args:
        obj: The annotation to convert.
        index: Root index of the created specification DataFrame.
        merge: Whether to merge all subtypes into a single row.
        separator: Separator for concatenating root and sub-indices.
        type: Name of the column for the metadata-stripped annotations.

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
        return _merge(_concat(frames)) if merge else _concat(frames)


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
