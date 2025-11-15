__all__ = ["from_dataclass", "from_typehint"]


# standard library
from collections.abc import Iterable
from dataclasses import fields
from typing import Annotated, Any


# dependencies
import pandas as pd
from .spec import Spec, SpecFrame, is_spec, to_specframe
from .typing import DataClass, get_annotated, get_annotations, get_subtypes


def from_dataclass(
    obj: DataClass,
    /,
    merge: bool = True,
    separator: str = "/",
) -> SpecFrame:
    """Create a specification DataFrame from given dataclass instance.

    Args:
        obj: The dataclass instance to convert.
        merge: Whether to merge all subtypes into a single row.
        separator: Separator for concatenating root and sub-indices.

    Returns:
        Created specification DataFrame.

    """
    frames: list[pd.DataFrame] = []

    for field in fields(obj):
        data = getattr(obj, field.name, field.default)
        frames.append(
            from_typehint(
                Annotated[field.type, Spec(data=data)],
                index=field.name,
                merge=merge,
                separator=separator,
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
) -> SpecFrame:
    """Create a specification DataFrame from given type hint.

    Args:
        obj: The type hint to convert.
        index: Root index of the created specification DataFrame.
        merge: Whether to merge all subtypes into a single row.
        separator: Separator for concatenating root and sub-indices.

    Returns:
        Created specification DataFrame.

    """
    annotated = get_annotated(obj, recursive=True)
    annotations = get_annotations(Annotated[obj, Spec(type=pd.NA)])
    frames: list[pd.DataFrame] = []
    specs: dict[str, Any] = {}

    for spec in filter(is_spec, annotations):
        specs.update(spec.fillna(annotated))

    frames.append(
        pd.DataFrame(
            data={key: [value] for key, value in specs.items()},
            index=pd.Index([index], name="index"),
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
    dummy: Any = object()
    columns = sorted(set[str]().union(*(df.columns for df in objs)))
    replaced = (df.reindex(columns=columns, fill_value=dummy) for df in objs)
    return pd.concat(replaced).replace({dummy: pd.NA})  # type: ignore


def _merge(obj: pd.DataFrame, /) -> pd.DataFrame:
    """Merge multiple rows of a DataFrame into a single row.

    Args:
        obj: DataFrame to merge.

    Returns:
        Merged DataFrame.

    """
    dummy: Any = object()
    replaced = obj.replace({float("nan"): dummy})  # type: ignore
    return replaced.bfill().replace({dummy: float("nan")}).head(1)  # type: ignore
