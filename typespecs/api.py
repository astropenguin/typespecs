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
    separator: str = "/",
) -> SpecFrame:
    """Create a specification DataFrame from given dataclass instance.

    Args:
        obj: The dataclass instance to convert.
        cast: Whether to convert column dtypes to nullable ones.
        merge: Whether to merge all subtypes into a single row.
        separator: Separator for concatenating root and sub-indices.

    Returns:
        Created specification DataFrame.

    """
    frames: list[SpecFrame] = []

    for field in fields(obj):
        data = getattr(obj, field.name, field.default)
        frames.append(
            from_typehint(
                Annotated[field.type, Spec(data=data)],
                cast=cast,
                index=field.name,
                merge=merge,
                separator=separator,
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
    separator: str = "/",
) -> SpecFrame:
    """Create a specification DataFrame from given type hint.

    Args:
        obj: The type hint to convert.
        cast: Whether to convert column dtypes to nullable ones.
        index: Root index of the created specification DataFrame.
        merge: Whether to merge all subtypes into a single row.
        separator: Separator for concatenating root and sub-indices.

    Returns:
        Created specification DataFrame.

    """
    annotated = get_annotated(obj, recursive=True)
    annotations = get_annotations(Annotated[obj, Spec(type=pd.NA)])
    frames: list[pd.DataFrame] = []
    specs: dict[str, Any] = {}

    for spec in filter(is_spec, annotations):
        specs.update(spec.fillna(annotated))

    frames.append(
        pd.DataFrame(
            data={key: [value] for key, value in specs.items()},
            index=pd.Index([index], name="index"),
        )
    )

    for subindex, subtype in enumerate(get_subtypes(obj)):
        frames.append(
            from_typehint(
                subtype,
                cast=False,
                index=f"{index}{separator}{subindex}",
                merge=False,
                separator=separator,
            )
        )

    if merge:
        frame = pd.concat(frames).bfill().head(1)
    else:
        frame = pd.concat(frames)

    if cast:
        return to_specframe(frame.convert_dtypes())
    else:
        return to_specframe(frame)
