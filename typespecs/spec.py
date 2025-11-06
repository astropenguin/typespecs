__all__ = ["Spec", "is_spec"]


# standard library
from typing import Any


# dependencies
import pandas as pd
from typing_extensions import Self, TypeGuard


class Spec(dict[str, Any]):
    """Type specification."""

    def fillna(self, value: Any, /) -> Self:
        """Fill missing values with given value."""
        return type(self)(
            (key, value if current is pd.NA else current)
            for key, current in self.items()
        )


def is_spec(obj: Any, /) -> TypeGuard[Spec]:
    """Check if given object is a type specification.

    Args:
        obj: The object to inspect.

    Returns:
        True if the object is a type specification. False otherwise.

    """
    return isinstance(obj, Spec)
