__all__ = ["coalesce", "concat", "default", "isna"]

# standard library
from collections.abc import Iterable, Mapping
from typing import Any, cast

# dependencies
import pandas as pd
from packaging.version import Version
from pandas import __version__ as PANDAS_VERSION


def coalesce(frame: pd.DataFrame, /) -> pd.DataFrame:
    """Coalesce multiple rows of a DataFrame into a single row.

    Args:
        frame: DataFrame to coalesce.

    Returns:
        Coalesced DataFrame (single row).
    """
    return frame.mask(isna(frame), frame.bfill()).head(1)


def concat(frames: Iterable[pd.DataFrame], /) -> pd.DataFrame:
    """Concatenate DataFrames row-wise with missing values filled with <NA>.

    Args:
        frames: DataFrames to concatenate.

    Returns:
        Concatenated DataFrame.
    """
    frames = list(frames)
    index = [idx for frame in frames for idx in frame.index]
    columns = sorted({col for frame in frames for col in frame.columns})
    concat = pd.DataFrame(pd.NA, index, columns, dtype=object)

    for frame in frames:
        concat.loc[frame.index, frame.columns] = frame

    return concat


def default(frame: pd.DataFrame, value: Mapping[str, Any] | Any, /) -> pd.DataFrame:
    """Fill missing values in given DataFrame with given value.

    Args:
        frame: DataFrame to fill.
        value: Default value for each column. Either a single value
            or a mapping of column names to values is accepted.

    Returns:
        DataFrame with missing values filled.
    """
    if isinstance(value, Mapping):
        values = cast(Mapping[str, Any], value)
    else:
        values = {key: value for key in frame.columns}

    missings = {key: pd.NA for key in set(values) - set(frame.columns)}
    replaces = {key: {pd.NA: val} for key, val in values.items()}
    return frame.assign(**missings).replace(replaces)


def isna(frame: pd.DataFrame, /) -> pd.DataFrame:
    """Detect missing values (<NA> only) in given DataFrame.

    Args:
        frame: DataFrame to check.

    Returns:
        Boolean DataFrame indicating missing values.
    """
    if Version(PANDAS_VERSION) >= Version("2.1"):
        return frame.map(lambda obj: obj is pd.NA)  # type: ignore
    else:
        return frame.applymap(lambda obj: obj is pd.NA)  # type: ignore
