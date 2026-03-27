__all__ = ["concat", "default", "merge", "replace"]

# standard library
from collections.abc import Iterable
from typing import Any, Mapping, TypeVar, cast

# dependencies
import pandas as pd
from packaging.version import Version

# type variables
TMapping = TypeVar("TMapping", bound=Mapping[Any, Any])


def concat(objs: Iterable[pd.DataFrame], /) -> pd.DataFrame:
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


def default(obj: pd.DataFrame, value: dict[str, Any] | Any, /) -> pd.DataFrame:
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


def merge(obj: pd.DataFrame, /) -> pd.DataFrame:
    """Merge multiple rows of a DataFrame into a single row.

    Args:
        obj: DataFrame to merge.

    Returns:
        Merged DataFrame.

    """
    if Version(pd.__version__) >= Version("2.1"):
        isna = obj.map(lambda obj: obj is pd.NA)  # type: ignore
    else:
        isna = obj.applymap(lambda obj: obj is pd.NA)  # type: ignore

    return obj.mask(isna, obj.bfill()).head(1)  # type: ignore


def replace(obj: TMapping, old: Any, new: Any, /) -> TMapping:
    """Replace the occurrences of a value in a mapping with new one.

    Args:
        obj: Mapping to replace.
        old: The value to be replaced.
        new: The value to replace with.

    Returns:
        New mapping with the replaced values.

    """
    return obj.__class__((k, new if v == old else v) for k, v in obj.items())
