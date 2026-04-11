__all__ = ["concat", "default", "merge"]

# standard library
from collections.abc import Iterable, Mapping
from typing import Any, cast

# dependencies
from packaging.version import Version
from pandas import NA, __version__ as PANDAS_VERSION, DataFrame, Index


def concat(frames: Iterable[DataFrame], /) -> DataFrame:
    """Concatenate DataFrames with missing values filled with <NA>.

    Args:
        frames: DataFrames to concatenate.

    Returns:
        Concatenated DataFrame.

    """
    indexes = [frame.index for frame in frames]
    columns = [frame.columns for frame in frames]
    concat = DataFrame(
        data=NA,
        index=Index([]).append(indexes),
        columns=Index([]).append(columns).unique().sort_values(),
        dtype=object,
    )

    for frame in frames:
        concat.loc[frame.index, frame.columns] = frame

    return concat


def default(frame: DataFrame, value: Mapping[str, Any] | Any, /) -> DataFrame:
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

    missings = {key: NA for key in set(values) - set(frame.columns)}
    replaces = {key: {NA: val} for key, val in values.items()}
    return frame.assign(**missings).replace(replaces)


def merge(frame: DataFrame, /) -> DataFrame:
    """Merge multiple rows of a DataFrame into a single row.

    Args:
        frame: DataFrame to merge.

    Returns:
        Merged DataFrame.

    """
    if Version(PANDAS_VERSION) >= Version("2.1"):
        isna = frame.map(lambda frame: frame is NA)  # type: ignore
    else:
        isna = frame.applymap(lambda frame: frame is NA)  # type: ignore

    return frame.mask(isna, frame.bfill()).head(1)  # type: ignore
