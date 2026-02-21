__all__ = ["ITSELF", "ItselfType", "Spec", "SpecFrame", "is_spec", "is_specframe"]


# standard library
from dataclasses import dataclass
from typing import Any


# dependencies
import pandas as pd
from typing_extensions import Self, TypeGuard


@dataclass(frozen=True)
class ItselfType:
    """Sentinel object specifying metadata-stripped annotation itself."""

    def __repr__(self) -> str:
        return "<ITSELF>"


ITSELF = ItselfType()
"""Sentinel object specifying metadata-stripped annotation itself."""


class Spec(dict[str, Any]):
    """Type specification.

    This class is essentially a dictionary and should be used
    to distinguish type specification from other type metadata.

    """

    def replace(self, old_value: Any, new_value: Any, /) -> Self:
        """Replace occurrences of old value with new value.

        Args:
            old_value: The value to be replaced.
            new_value: The value to replace with.

        Returns:
            Replaced type specification.

        """
        return type(self)(
            (key, new_value if value == old_value else value)
            for key, value in self.items()
        )


class SpecFrame(pd.DataFrame):
    """Specification DataFrame.

    This class is essentially a pandas DataFrame and should be used
    to distinguish specification DataFrame from other DataFrames.

    """


def is_spec(obj: Any, /) -> TypeGuard[Spec]:
    """Check if given object is a type specification.

    Args:
        obj: Object to inspect.

    Returns:
        True if the object is a type specification. False otherwise.

    """
    return isinstance(obj, Spec)


def is_specframe(obj: Any, /) -> TypeGuard[SpecFrame]:
    """Check if given object is a specification DataFrame.

    Args:
        obj: Object to inspect.

    Returns:
        True if the object is a specification DataFrame. False otherwise.

    """
    return isinstance(obj, SpecFrame)
