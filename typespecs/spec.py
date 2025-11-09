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

    def fillna(self, value: Any, /) -> Self:
        """Fill missing values with given value."""
        return type(self)(
            (key, value if current is pd.NA else current)
            for key, current in self.items()
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

    def ensure(self, **defaults: Any) -> SpecFrame:
        """Ensure given columns exist with their default values.

        This method fills existing columns with their default values
        where missing, and adds missing columns with their default values.

        Args:
            **defaults: Default values for columns to ensure.

        Returns:
            Specification DataFrame with ensured columns.

        """
        existing: dict[str, Any] = {}
        missing: dict[str, Any] = {}

        for key, value in defaults.items():
            if key in self.accessed.columns:
                existing[key] = value
            else:
                missing[key] = value

        return self.accessed.fillna(existing).assign(**missing)  # type: ignore


def is_spec(obj: Any, /) -> TypeGuard[Spec]:
    """Check if given object is a type specification.

    Args:
        obj: Object to inspect.

    Returns:
        True if the object is a type specification. False otherwise.

    """
    return isinstance(obj, Spec)


def to_specframe(dataframe: pd.DataFrame, /) -> SpecFrame:
    """Cast given DataFrame to specification DataFrame.

    Args:
        dataframe: DataFrame to cast.

    Returns:
        Cast specification DataFrame.

    """
    return cast(SpecFrame, dataframe)
