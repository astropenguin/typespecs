__all__ = ["Spec", "SpecFrame", "SpecFrameAccessor", "is_spec", "to_specframe"]


# standard library
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, cast


# dependencies
import pandas as pd
from pandas.api.extensions import register_dataframe_accessor
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


if TYPE_CHECKING:

    class SpecFrame(pd.DataFrame):
        """Specification DataFrame.

        This class is only for type hinting purposes.
        At runtime, it becomes equivalent to pandas.DataFrame.

        """

        spec: "SpecFrameAccessor"
        """Accessor for specification DataFrame."""

else:
    SpecFrame = pd.DataFrame


@register_dataframe_accessor("spec")
@dataclass(frozen=True)
class SpecFrameAccessor:
    """Accessor for specification DataFrame.

    Args:
        accessed: Specification DataFrame to access.

    """

    accessed: SpecFrame
    """Specification DataFrame to access."""

    def __getitem__(self, key: str, /) -> pd.Series:
        """Return specification column by given key.

        Args:
            key: Key of the specification column to get.

        Returns:
            Specification column with the given key.
            If the key does not exist, a Series filled with <NA>
            will be returned instead of a KeyError being raised.

        """
        if key in self.accessed:
            return self.accessed[key]
        else:
            return pd.Series(
                data=pd.NA,
                index=self.accessed.index,
                name=key,
            )


def is_spec(obj: Any, /) -> TypeGuard[Spec]:
    """Check if given object is a type specification.

    Args:
        obj: Object to inspect.

    Returns:
        True if the object is a type specification. False otherwise.

    """
    return isinstance(obj, Spec)


def to_specframe(obj: pd.DataFrame, /) -> SpecFrame:
    """Cast given DataFrame to specification DataFrame.

    Args:
        obj: DataFrame to cast.

    Returns:
        Cast specification DataFrame.

    """
    return cast(SpecFrame, obj)
