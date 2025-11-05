__all__ = ["Attr", "from_dataclass", "from_typehint", "is_attr"]


# standard library
from collections.abc import Hashable
from dataclasses import dataclass, fields, replace
from typing import Annotated as Ann, Any


# dependencies
import pandas as pd
from .typing import DataClass, gen_subtypes, get_annotated, get_annotations
from typing_extensions import Self, TypeGuard


@dataclass(frozen=True)
class Attr:
    """Typespec attribute.

    Args:
        key: Attribute key.
        value: Attribute value. <NA> indicates a key-only attribute.

    """

    key: Hashable
    """Attribute key."""

    value: Any = pd.NA
    """Attribute value. <NA> indicates a key-only attribute."""

    def fillna(self, value: Any, /) -> Self:
        """Fill missing attribute value with given value."""
        if self.value is pd.NA:
            return replace(self, value=value)
        else:
            return replace(self)


def from_dataclass(obj: DataClass, /, merge: bool = True) -> pd.DataFrame:
    """Create a typespec DataFrame from given dataclass instance.

    Args:
        obj: The dataclass instance to convert.
        merge: Whether to merge all subtypes into a single row.

    Returns:
        The resulting typespec DataFrame.

    """
    specs: list[pd.DataFrame] = []

    for field in fields(obj):
        data = getattr(obj, field.name, field.default)
        specs.append(
            from_typehint(
                Ann[field.type, Attr("data", data)],
                index=field.name,
                merge=merge,
            )
        )

    return pd.concat(specs)


def from_typehint(
    obj: Any,
    /,
    *,
    index: str = "root",
    merge: bool = True,
) -> pd.DataFrame:
    """Create a typespec DataFrame from given type hint.

    Args:
        obj: The type hint to convert.
        index: The index label for the resulting DataFrame.
        merge: Whether to merge all subtypes into a single row.

    Returns:
        The resulting typespec DataFrame.

    """
    attrs: dict[Hashable, Any] = {}
    specs: list[pd.DataFrame] = []
    annotated = get_annotated(obj, recursive=True)
    annotations = get_annotations(Ann[obj, Attr("type")])

    for attr in filter(is_attr, annotations):
        attrs[attr.key] = attr.fillna(annotated).value

    specs.append(
        pd.DataFrame(
            columns=list(attrs.keys()),
            data=[list(attrs.values())],
            index=pd.Index([index], name="index"),
        ).convert_dtypes(),
    )

    for subindex, subtype in enumerate(gen_subtypes(obj)):
        specs.append(
            from_typehint(
                subtype,
                index=f"{index}.{subindex}",
                merge=False,
            )
        )

    if merge:
        return pd.concat(specs).bfill().head(1)
    else:
        return pd.concat(specs)


def is_attr(obj: Any, /) -> TypeGuard[Attr]:
    """Check if given object is a typespec attribute."""
    return isinstance(obj, Attr)
