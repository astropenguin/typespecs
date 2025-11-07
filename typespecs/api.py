__all__ = ["from_dataclass", "from_typehint"]


# standard library
from dataclasses import fields
from typing import Annotated, Any


# dependencies
import pandas as pd
from .spec import Spec, SpecFrame, is_spec, to_specframe
from .typing import DataClass, get_annotated, get_annotations, get_subtypes


def from_dataclass(
    obj: DataClass,
    /,
    cast: bool = True,
    merge: bool = True,
) -> SpecFrame:
    """Create a specification DataFrame from given dataclass instance.

    Args:
        obj: The dataclass instance to convert.
        cast: Whether to convert column dtypes to nullable ones.
        merge: Whether to merge all subtypes into a single row.

    Returns:
        Created specification DataFrame.

    """
    frames: list[pd.DataFrame] = []

    for field in fields(obj):
        data = getattr(obj, field.name, field.default)
        frames.append(
            from_typehint(
                Annotated[field.type, Spec(data=data)],
                cast=cast,
                index=field.name,
                merge=merge,
            )
        )

    return to_specframe(pd.concat(frames))


def from_typehint(
    obj: Any,
    /,
    *,
    cast: bool = True,
    index: str = "root",
    merge: bool = True,
) -> SpecFrame:
    """Create a specification DataFrame from given type hint.

    Args:
        obj: The type hint to convert.
        cast: Whether to convert column dtypes to nullable ones.
        index: Root index of the created specification DataFrame.
        merge: Whether to merge all subtypes into a single row.

    Returns:
        Created specification DataFrame.

    """
    annotated = get_annotated(obj, recursive=True)
    annotations = get_annotations(Annotated[obj, Spec(type=pd.NA)])
    frames: list[pd.DataFrame] = []
    specs: dict[str, Any] = {}

    for spec in filter(is_spec, annotations):
        specs.update(spec.fillna(annotated))

    frame = pd.DataFrame(
        data={key: [value] for key, value in specs.items()},
        index=pd.Index([index], name="index"),
    )

    if cast:
        frames.append(frame.convert_dtypes())
    else:
        frames.append(frame)

    for subindex, subtype in enumerate(get_subtypes(obj)):
        frames.append(
            from_typehint(
                subtype,
                cast=cast,
                index=f"{index}.{subindex}",
                merge=False,
            )
        )

    if merge:
        return to_specframe(pd.concat(frames)).bfill().head(1)
    else:
        return to_specframe(pd.concat(frames))
