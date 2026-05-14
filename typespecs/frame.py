__all__ = ["concat", "fillna", "isna", "no_silent_downcasting", "rollup"]

# standard library
from collections.abc import Callable, Iterable, Mapping
from contextlib import AbstractContextManager, nullcontext
from functools import partial, reduce
from typing import Any, Literal

# dependencies
import pandas as pd
from packaging.version import Version
from pandas import __version__ as PANDAS_VERSION

# type hints
Resolution = Callable[[Any, Any], Any] | Literal["override", "update"]


def concat(frames: Iterable[pd.DataFrame], /) -> pd.DataFrame:
    """Concatenate DataFrames row-wise with missing values filled with ``<NA>``.

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


def fillna(frame: pd.DataFrame, value: Mapping[str, Any] | Any, /) -> pd.DataFrame:
    """Fill missing values (``<NA>`` only) in given DataFrame with given value.

    Args:
        frame: DataFrame to fill.
        value: Default value for each column. Either a single value
            or a mapping of column names to values is accepted.
            If the specified columns are not present in ``frame``,
            each column filled with the specified value will be added.

    Returns:
        DataFrame with missing values (``<NA>`` only) filled.
    """
    frame = frame.copy()
    values: dict[str, Any]

    if isinstance(value, Mapping):
        values = dict(value)  # type: ignore
    else:
        values = {col: value for col in frame.columns}

    for col in set(values) - set(frame.columns):
        frame[col] = pd.Series(pd.NA, frame.index, dtype=object)

    replacements = pd.Series(
        [values.get(col, pd.NA) for col in frame.columns],
        frame.columns,
        dtype=object,
    )
    return frame.mask(isna(frame), replacements, axis=1)


def isna(frame: pd.DataFrame, /) -> pd.DataFrame:
    """Detect missing values (``<NA>`` only) in given DataFrame.

    Args:
        frame: DataFrame to check.

    Returns:
        Boolean DataFrame indicating missing values (``<NA>`` only).
    """
    if Version(PANDAS_VERSION) >= Version("2.1"):
        return frame.map(lambda obj: obj is pd.NA)  # type: ignore
    else:
        return frame.applymap(lambda obj: obj is pd.NA)  # type: ignore


def no_silent_downcasting() -> AbstractContextManager[None]:
    """Context manager to avoid silent downcasting for pandas < 3."""
    if Version(PANDAS_VERSION) >= Version("3"):
        return nullcontext()
    else:
        return pd.option_context("future.no_silent_downcasting", True)


def rollup(
    frame: pd.DataFrame,
    conflict: Mapping[str, Resolution] | Resolution = "override",
    /,
) -> pd.DataFrame:
    """Roll-up given DataFrame by resolving conflicts between rows.

    Args:
        frame: DataFrame to roll up.
        conflict: Resolution strategy for conflicts between rows.
            Either a single resolution or a mapping of column names
            to resolutions is accepted. As built-in resolutions,
            ``"override"`` (new value overrides old value; default behavior)
            and ``"update"`` (new mapping updates old mapping) are supported.
            A function that takes old and new values and returns
            resolved value can also be accepted as a custom resolution.

    Returns:
        Rolled-up DataFrame.
    """

    def override(old: Any, new: Any, /) -> Any:
        return old if new is pd.NA else new

    def update(old: Any, new: Any, /) -> Any:
        if old is pd.NA or new is pd.NA:
            return override(old, new)
        else:
            return type(new)({**old, **new})

    reducers: dict[str, Callable[[pd.Series], Any]] = {}
    resolutions: dict[str, Resolution]

    if isinstance(conflict, Mapping):
        resolutions = {col: conflict.get(col, override) for col in frame.columns}
    else:
        resolutions = {col: conflict for col in frame.columns}

    for col, resolution in resolutions.items():
        if resolution == "override":
            reducers[col] = partial(reduce, override)
        elif resolution == "update":
            reducers[col] = partial(reduce, update)
        else:
            reducers[col] = partial(reduce, resolution)

    return pd.DataFrame([frame[::-1].agg(reducers)], frame.index[:1], dtype=object)
