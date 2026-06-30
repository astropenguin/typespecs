__all__ = [
    "collapse",
    "concat",
    "fillna",
    "isna",
    "no_silent_downcasting",
    "replace",
]

# standard library
from collections.abc import Callable, Iterable, Mapping
from contextlib import AbstractContextManager, nullcontext
from functools import reduce
from typing import Any, Literal
from warnings import warn

# dependencies
import pandas as pd
from packaging.version import Version
from pandas import __version__ as PANDAS_VERSION

# type hints
Resolution = Literal["override", "update"] | Callable[[Any, Any], Any]


def collapse(
    frame: pd.DataFrame,
    conflict: Mapping[str, Resolution] | Resolution = "override",
    /,
) -> pd.DataFrame:
    """Collapse given DataFrame by resolving conflicts between rows.

    Args:
        frame: DataFrame to collapse.
        conflict: Resolution strategy for conflicts between rows.
            Either a single resolution or a mapping of column names
            to resolutions is accepted. As built-in resolutions,
            ``"override"`` (new value overrides old value; default behavior)
            and ``"update"`` (new mapping updates old mapping) are supported.
            A function that takes old and new values and returns
            resolved value can also be accepted as a custom resolution.

    Returns:
        Collapsed DataFrame.
    """

    def override(old: Any, new: Any, /) -> Any:
        return old if new is pd.NA else new

    def update(old: Any, new: Any, /) -> Any:
        if old is pd.NA or new is pd.NA:
            return override(old, new)
        else:
            return type(new)({**old, **new})

    builtins: dict[str, Any] = {"override": override, "update": update}
    conflicts: dict[str, Any]

    if isinstance(conflict, Mapping):
        conflicts = {
            column: builtins.get(resolution, resolution)
            for column, resolution in conflict.items()  # type: ignore
        }
    else:
        conflicts = dict.fromkeys(
            frame.columns,
            builtins.get(conflict, conflict),  # type: ignore
        )

    reduced = {
        column: reduce(conflicts.get(column, override), frame[column])
        for column in frame.columns
    }
    return (
        # fmt: off
        pd.DataFrame([reduced], frame.index[-1:], dtype=object)
        .astype(frame.dtypes, errors="ignore")
        # fmt: on
    )


def concat(frames: Iterable[pd.DataFrame], /) -> pd.DataFrame:
    """Concatenate DataFrames row-wise with missing values filled with ``<NA>``.

    Args:
        frames: DataFrames to concatenate.

    Returns:
        Concatenated DataFrame.
    """
    frames = list(frames)
    values = {column: pd.NA for frame in frames for column in frame.columns}
    filled = (fillna(frame, values) for frame in frames)

    if Version(PANDAS_VERSION) >= Version("3"):
        return pd.concat(filled).sort_index(axis=1)
    else:
        dummy = object()
        concat = pd.concat(
            # fmt: off
            replace(frame, pd.NA, dummy, on=object)
            for frame in filled
            # fmt: on
        )
        return (
            # fmt: off
            replace(concat, dummy, pd.NA, on=object)
            .sort_index(axis=1)
            # fmt: on
        )


def fillna(
    frame: pd.DataFrame,
    value: Mapping[str, Any] | Any = pd.NA,
    /,
) -> pd.DataFrame:
    """Fill pandas ``<NA>`` in given DataFrame with given value.

    Args:
        frame: DataFrame to fill.
        value: Default value for each column. Either a single value
            or a mapping of column names to values is accepted.
            If the specified columns are not present in ``frame``,
            each column filled with the specified value will be added.

    Returns:
        Filled DataFrame.
    """
    frame = frame.copy()
    dtypes = frame.dtypes.copy()

    if isinstance(value, Mapping):
        values = dict(value)  # type: ignore
    else:
        values = dict.fromkeys(frame.columns, value)

    frame[list(set(values) - set(frame.columns))] = pd.NA

    for column, value in values.items():
        if any(row := [obj is pd.NA for obj in frame[column]]):
            frame.loc[row, column] = value

    return frame.astype(dtypes, errors="ignore")


def isna(frame: pd.DataFrame, /) -> pd.DataFrame:
    """Detect missing values (``<NA>`` only) in given DataFrame.

    Args:
        frame: DataFrame to check.

    Returns:
        Boolean DataFrame indicating missing values (``<NA>`` only).
    """
    warn(
        "This function will be deprecated in the next major version."
        "Use ``map(frame, lambda obj: obj is pandas.NA)`` instead.",
        DeprecationWarning,
    )
    return frame.map(lambda obj: obj is pd.NA)  # type: ignore


def no_silent_downcasting() -> AbstractContextManager[None]:
    """Context manager to avoid silent downcasting for pandas < 3."""
    warn(
        "This function will be deprecated in the next major version.",
        DeprecationWarning,
    )
    if Version(PANDAS_VERSION) >= Version("3"):
        return nullcontext()
    else:
        return pd.option_context("future.no_silent_downcasting", True)


def replace(
    frame: pd.DataFrame,
    old: Any,
    new: Any,
    /,
    on: Any | None = None,
) -> pd.DataFrame:
    """Replace old value with new value in given DataFrame.

    Args:
        frame: DataFrame to replace.
        old: Old value to replace.
        new: New value to replace with.
        on: Optional data type to restrict replacement on.

    Returns:
        Replaced DataFrame.
    """
    frame = frame.copy()
    dtypes = frame.dtypes.copy()

    for column in frame.columns:
        if on is None or frame[column].dtype == on:
            if old is pd.NA:
                if any(row := [obj is pd.NA for obj in frame[column]]):
                    frame.loc[row, column] = new
            else:
                if any(row := [obj == old for obj in frame[column]]):
                    frame.loc[row, column] = new

    return frame.astype(dtypes, errors="ignore")
