__all__ = ["Spec", "is_spec"]


# standard library
from typing import Any


# dependencies
from typing_extensions import Self, TypeGuard


class Spec(dict[str, Any]):
    """Type specification.

    This class is essentially a dictionary and should be used
    to distinguish type specification from other type annotations.

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


def is_spec(obj: Any, /) -> TypeGuard[Spec]:
    """Check if given object is a type specification.

    Args:
        obj: Object to inspect.

    Returns:
        True if the object is a type specification. False otherwise.

    """
    return isinstance(obj, Spec)
