__all__ = ["fill", "group", "merge", "pop", "sort"]

# standard library
from collections import defaultdict
from collections.abc import Callable, Hashable, Iterable, Mapping, MutableMapping
from itertools import product
from typing import Any, Literal, Protocol, TypeVar, cast

# dependencies
import pandas as pd

# type hints
TKey = TypeVar("TKey", bound=Hashable)
TValue = TypeVar("TValue")
TMapping = TypeVar("TMapping", bound=Mapping[Hashable, Any])
Multiple = Mapping[Hashable, TValue] | TValue
Resolver = Callable[[Any, Any], Any] | Literal["override", "update"]


class SortKey(Protocol):
    """Protocol for keys for sorting."""

    def __lt__(self, other: Any, /) -> bool: ...


def fill(
    mappings: Iterable[Mapping[TKey, TValue]],
    filler: Multiple[Any],
    /,
) -> list[dict[Hashable, Any]]:
    """Fill missing keys in the given mappings.

    Args:
        mappings: Iterable of mappings to fill.
        filler: Value(s) to fill missing keys with.

    Returns:
        List of filled mappings.
    """
    mappings = list(mappings)
    fillers: Mapping[Hashable, Any]

    if isinstance(filler, Mapping):
        fillers = dict.fromkeys(keys_of(mappings), pd.NA)
        fillers.update(cast(Mapping[Hashable, Any], filler))
    else:
        fillers = dict.fromkeys(keys_of(mappings), filler)

    filled = cast(
        list[dict[Hashable, Any]],
        [dict(mapping) for mapping in mappings],
    )

    for mapping, key in product(filled, fillers):
        mapping.setdefault(key, fillers[key])

    return filled


def group(
    mappings: Iterable[TMapping],
    key: Hashable | Callable[[TMapping], Hashable],
    /,
) -> list[list[TMapping]]:
    """Group the given mappings by the given key.

    Args:
        mappings: Iterable of mappings to group.
        key: Key or function to group by.

    Returns:
        List of groups of mappings.
    """

    def key_of(mapping: TMapping, /) -> Hashable:
        return key(mapping) if callable(key) else mapping[key]

    groups: dict[Hashable, list[TMapping]] = defaultdict(list)

    for mapping in mappings:
        groups[key_of(mapping)].append(mapping)

    return list(groups.values())


def merge(
    mappings: Iterable[Mapping[TKey, TValue]],
    resolver: Multiple[Resolver],
    /,
) -> dict[TKey, TValue]:
    """Merge the given mappings into a single dictionary.

    Args:
        mappings: Iterable of mappings to merge.
        resolver: Function(s) to resolve conflicts.

    Returns:
        Merged dictionary.
    """
    mappings = list(mappings)
    resolvers: Mapping[Hashable, Resolver]

    if isinstance(resolver, Mapping):
        resolvers = dict.fromkeys(keys_of(mappings), override)
        resolvers.update(cast(Mapping[Hashable, Resolver], resolver))
    else:
        resolvers = dict.fromkeys(keys_of(mappings), resolver)

    merged: dict[TKey, TValue] = {}

    for mapping in mappings:
        for key, val in mapping.items():
            if (resolver := resolvers[key]) == "override":
                resolver = override

            if resolver == "update":
                resolver = update

            merged[key] = resolver(merged.get(key, pd.NA), val)

    return merged


def pop(
    mappings: Iterable[MutableMapping[TKey, TValue]],
    key: TKey,
    /,
) -> list[TValue]:
    """Remove a key from the given mappings in-place.

    Args:
        mappings: Iterable of mappings to remove the key from.
        key: Key to be removed.

    Returns:
        List of removed values.
    """
    popped: list[TValue] = []

    for mapping in mappings:
        if key in mapping:
            popped.append(mapping.pop(key))

    return popped


def sort(
    mappings: Iterable[TMapping],
    key: Hashable | Callable[[TMapping], SortKey],
    /,
    *,
    reverse: bool = False,
) -> list[TMapping]:
    """Sort the given mappings.

    Args:
        mappings: Iterable of mappings to sort.
        key: Key or function to sort by.
        reverse: Whether to sort in reverse order.

    Returns:
        List of sorted mappings.
    """

    def key_of(mapping: TMapping, /) -> SortKey:
        return key(mapping) if callable(key) else mapping[key]

    return sorted(mappings, key=key_of, reverse=reverse)


def keys_of(mappings: Iterable[Mapping[TKey, Any]], /) -> set[TKey]:
    """Return a set of all keys in the given mappings."""
    return {key for mapping in mappings for key in mapping}


def override(old: Any, new: Any, /) -> Any:
    """Override the old value with the new value."""
    return old if new is pd.NA else new


def update(old: Any, new: Any, /) -> Any:
    """Update the old value with the new value."""
    if old is pd.NA or new is pd.NA:
        return override(old, new)
    else:
        return {**old, **new}
