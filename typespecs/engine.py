__all__ = ["fill", "group", "merge", "pop", "rename", "sort"]

# standard library
from collections import defaultdict
from collections.abc import Callable, Hashable, Iterable, Mapping
from typing import Any, Literal, TypeVar, cast

# dependencies
import pandas as pd

# type hints
TAny = TypeVar("TAny")
Multiple = Mapping[str, TAny] | TAny
Resolver = Callable[[Any, Any], Any] | Literal["override", "update"]


def fill(
    strdicts: Iterable[dict[str, Any]],
    filler: Multiple[Any] = pd.NA,
    /,
) -> list[dict[str, Any]]:
    """Fill missing keys in the given string-key dicts.

    Args:
        strdicts: Iterable of string-key dicts to fill.
        filler: Value(s) to fill missing keys with.

    Returns:
        List of filled string-key dicts.
    """
    strdicts = list(strdicts)
    fillers: dict[str, Any]

    if isinstance(filler, Mapping):
        fillers = cast(dict[str, Any], filler)
    else:
        fillers = dict.fromkeys(keys_of(strdicts), filler)

    filled = [strdict.copy() for strdict in strdicts]

    for key in keys_of(filled) | fillers.keys():
        for strdict in filled:
            if key not in strdict:
                strdict[key] = fillers.get(key, pd.NA)

    return filled


def group(
    strdicts: Iterable[dict[str, Any]],
    key: Callable[[dict[str, Any]], Any] | str,
    /,
) -> list[list[dict[str, Any]]]:
    """Group the given string-key dicts.

    Args:
        strdicts: Iterable of string-key dicts to group.
        key: Key or function to group by.

    Returns:
        List of groups of string-key dicts.
    """

    def key_of(strdict: dict[str, Any], /) -> Hashable:
        match key:
            case str():
                return strdict[key]
            case Callable():
                return key(strdict)
            case _:
                raise ValueError(f"Invalid key: {key!r}")

    groups: dict[Hashable, list[dict[str, Any]]] = defaultdict(list)

    for strdict in strdicts:
        groups[key_of(strdict)].append(strdict)

    return list(groups.values())


def merge(
    strdicts: Iterable[dict[str, Any]],
    resolver: Multiple[Resolver] = "override",
    /,
) -> dict[str, Any]:
    """Merge the given string-key dicts into a single one.

    Args:
        strdicts: Iterable of string-key dicts to merge.
        resolver: Function(s) to resolve conflicts.

    Returns:
        Merged string-key dict.
    """
    strdicts = list(strdicts)
    resolvers: dict[str, Resolver]

    if isinstance(resolver, Mapping):
        resolvers = cast(dict[str, Resolver], resolver)
    else:
        resolvers = dict.fromkeys(keys_of(strdicts), resolver)

    merged: dict[str, Any] = {}

    for strdict in strdicts:
        for key, val in strdict.items():
            resolver = resolvers.get(key, override)

            if resolver == "override":
                resolver = override

            if resolver == "update":
                resolver = update

            if key in merged:
                merged[key] = resolver(merged[key], val)
            else:
                merged[key] = val

    return merged


def pop(
    strdicts: Iterable[dict[str, Any]],
    key: str,
    /,
) -> list[Any]:
    """Remove a key from the given string-key dicts.

    Args:
        strdicts: Iterable of string-key dicts to remove.
        key: Key to be removed.

    Returns:
        List of removed values.
    """
    popped: list[Any] = []

    for strdict in strdicts:
        if key in strdict:
            popped.append(strdict.pop(key))

    return popped


def rename(
    strdicts: Iterable[dict[str, Any]],
    old: str,
    new: str,
    /,
) -> list[dict[str, Any]]:
    """Rename a key in the given string-key dicts.

    Args:
        strdicts: Iterable of string-key dicts to rename.
        old: Old key to rename from.
        new: New key to rename to.

    Returns:
        List of renamed string-key dicts.
    """
    renamed = [strdict.copy() for strdict in strdicts]

    for strdict in renamed:
        if old in strdict:
            strdict[new] = strdict.pop(old)

    return renamed


def sort(
    strdicts: Iterable[dict[str, Any]],
    key: Callable[[dict[str, Any]], Any] | str,
    /,
    *,
    reverse: bool = False,
) -> list[dict[str, Any]]:
    """Sort the given string-key dicts.

    Args:
        strdicts: Iterable of string-key dicts to sort.
        key: Key or function to sort by.
        reverse: Whether to sort in reverse order.

    Returns:
        List of sorted string-key dicts.
    """

    def key_of(strdict: dict[str, Any], /) -> Any:
        match key:
            case str():
                return strdict[key]
            case Callable():
                return key(strdict)
            case _:
                raise ValueError(f"Invalid key: {key!r}")

    return sorted(strdicts, key=key_of, reverse=reverse)


def keys_of(strdicts: Iterable[dict[str, Any]], /) -> set[str]:
    """Return a set of all keys in the given string-key dicts."""
    return {key for strdict in strdicts for key in strdict}


def override(old: Any, new: Any, /) -> Any:
    """Override the old value with the new value."""
    return old if new is pd.NA else new


def update(old: Any, new: Any, /) -> Any:
    """Update the old value with the new value."""
    if old is pd.NA or new is pd.NA:
        return override(old, new)
    else:
        return {**old, **new}
