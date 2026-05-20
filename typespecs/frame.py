__all__ = ["collapse", "concat", "fillna", "isna", "no_silent_downcasting"]

# standard library
from collections.abc import Callable, Iterable, Mapping
from contextlib import AbstractContextManager, nullcontext
from functools import reduce
from typing import Any, Literal

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
            col: builtins.get(resolution, resolution)
            for col, resolution in conflict.items()  # type: ignore
        }
    else:
        conflicts = dict.fromkeys(
            frame.columns,
            builtins.get(conflict, conflict),  # type: ignore
        )

    reduced = {
        # fmt: off
        col: reduce(conflicts.get(col, override), frame[col])
        for col in frame.columns
        # fmt: on
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
    concat = pd.DataFrame(
        pd.NA,
        [idx for frame in frames for idx in frame.index],
        sorted({col for frame in frames for col in frame.columns}),
        dtype=object,
    )

    for frame in frames:
        concat.loc[frame.index, frame.columns] = frame

    return concat


def fillna(
    frame: pd.DataFrame,
    value: Mapping[str, Any] | Any = pd.NA,
    /,
) -> pd.DataFrame:
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
        values = dict.fromkeys(frame.columns, value)

    for col in set(values) - set(frame.columns):
        frame[col] = pd.Series(pd.NA, frame.index, dtype=object)

    replacements = pd.Series(
        [values.get(col, pd.NA) for col in frame.columns],
        frame.columns,
        dtype=object,
    )
    return (
        # fmt: off
        frame
        .mask(isna(frame), replacements, axis=1)
        .astype(frame.dtypes, errors="ignore")
        # fmt: on
    )


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
