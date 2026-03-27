__all__ = ["ITSELF", "ItselfType", "Spec", "SpecFrame", "is_spec", "is_specframe"]

# standard library
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, overload

# dependencies
import pandas as pd
from readonlydict import ReadonlyDict
from typing_extensions import Self, TypeGuard


@dataclass(frozen=True)
class ItselfType:
    """Sentinel object specifying metadata-stripped annotation itself."""

    __array_ufunc__ = None

    def __repr__(self) -> str:
        return "<ITSELF>"


ITSELF = ItselfType()
"""Sentinel object specifying metadata-stripped annotation itself."""


class Spec(ReadonlyDict[str, Any]):
    """Type specification.

    This is a subclass of the read-only dictionary without any runtime modifications.
    It is intended to distinguish a type specification from other type metadata.

    """

    if TYPE_CHECKING:
        # fmt: off
        @overload
        def __new__(cls, **kwargs: Any) -> Self:...
        @overload
        def __new__(cls, mapping: Mapping[str, Any], /, **kwargs: Any) -> Self: ...
        @overload
        def __new__(cls, iterable: Iterable[tuple[str, Any]], /, **kwargs: Any) -> Self: ...
        # fmt: on

        @overload
        @classmethod
        def fromkeys(cls, iterable: Iterable[str], /) -> Self: ...
        @overload
        @classmethod
        def fromkeys(cls, iterable: Iterable[str], value: Any, /) -> Self: ...

        def __or__(self, other: Mapping[str, Any], /) -> Self: ...


class SpecFrame(pd.DataFrame):
    """Specification DataFrame.

    This is a subclass of the pandas DataFrame without any runtime modifications.
    It is intended to distinguish a specification DataFrame from other DataFrames.

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
