__all__ = ["Attrs", "from_dataclass", "from_typehint", "is_attrs"]


# standard library
from dataclasses import fields
from typing import Annotated as Ann, Any


# dependencies
import pandas as pd
from .typing import DataClass, gen_subtypes, get_annotated, get_annotations
from typing_extensions import Self, TypeGuard


class Attrs(dict[str, Any]):
    """Typespec attributes."""

    def fillna(self, value: Any, /) -> Self:
        """Fill missing attribute values with given value."""
        return type(self)(
            (key, value if current is pd.NA else current)
            for key, current in self.items()
        )


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
                Ann[field.type, Attrs(data=data)],
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
    attrs = Attrs()
    specs: list[pd.DataFrame] = []
    annotated = get_annotated(obj, recursive=True)
    annotations = get_annotations(Ann[obj, Attrs(type=pd.NA)])

    for attrs_ in filter(is_attrs, annotations):
        attrs.update(attrs_.fillna(annotated))

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


def is_attrs(obj: Any, /) -> TypeGuard[Attrs]:
    """Check if given object is a typespec attributes."""
    return isinstance(obj, Attrs)
