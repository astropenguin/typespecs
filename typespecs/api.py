__all__ = ["ITSELF", "ItselfType", "from_dataclass", "from_typehint"]


# standard library
from collections.abc import Iterable
from dataclasses import dataclass, fields
from typing import Annotated, Any


# dependencies
import pandas as pd
from .spec import Spec, SpecFrame, is_spec, to_specframe
from .typing import DataClass, get_annotated, get_annotations, get_subtypes


@dataclass(frozen=True)
class ItselfType:
    """Sentinel object representing annotated type itself."""

    def __repr__(self) -> str:
        return "<ITSELF>"


ITSELF = ItselfType()
"""Sentinel object representing annotated type itself."""


def from_dataclass(
    obj: DataClass,
    /,
    data: str = "data",
    merge: bool = True,
    separator: str = "/",
    type: str = "type",
) -> SpecFrame:
    """Create a specification DataFrame from given dataclass instance.

    Args:
        obj: The dataclass instance to convert.
        data: Column name of field data in the specification DataFrame.
        merge: Whether to merge all subtypes into a single row.
        separator: Separator for concatenating root and sub-indices.
        type: Column name of field types in the specification DataFrame.

    Returns:
        Created specification DataFrame.

    """
    frames: list[pd.DataFrame] = []

    for field in fields(obj):
        data_ = getattr(obj, field.name, field.default)
        frames.append(
            from_typehint(
                Annotated[field.type, Spec({data: data_})],
                index=field.name,
                merge=merge,
                separator=separator,
                type=type,
            )
        )

    with pd.option_context("future.no_silent_downcasting", True):
        return to_specframe(_concat(frames))


def from_typehint(
    obj: Any,
    /,
    *,
    index: str = "root",
    merge: bool = True,
    separator: str = "/",
    type: str = "type",
) -> SpecFrame:
    """Create a specification DataFrame from given type hint.

    Args:
        obj: The type hint to convert.
        index: Root index of the created specification DataFrame.
        merge: Whether to merge all subtypes into a single row.
        separator: Separator for concatenating root and sub-indices.
        type: Column name of the type hint in the specification DataFrame.

    Returns:
        Created specification DataFrame.

    """
    annotated = get_annotated(obj, recursive=True)
    annotations = get_annotations(Annotated[obj, Spec({type: ITSELF})])
    frames: list[pd.DataFrame] = []
    specs: dict[str, Any] = {}

    for spec in filter(is_spec, annotations):
        specs.update(spec.replace(ITSELF, annotated))

    frames.append(
        pd.DataFrame(
            data={key: [value] for key, value in specs.items()},
            index=[index],
            dtype=object,
        )
    )

    for subindex, subtype in enumerate(get_subtypes(obj)):
        frames.append(
            from_typehint(
                subtype,
                index=f"{index}{separator}{subindex}",
                merge=False,
                separator=separator,
                type=type,
            )
        )

    with pd.option_context("future.no_silent_downcasting", True):
        if merge:
            return to_specframe(_merge(_concat(frames)))
        else:
            return to_specframe(_concat(frames))


def _concat(objs: Iterable[pd.DataFrame], /) -> pd.DataFrame:
    """Concatenate multiple DataFrames with missing values filled with <NA>.

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
    return obj.mask(obj.map(_isna), obj.bfill()).head(1)
