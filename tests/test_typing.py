# standard library
from typing import Annotated as Ann, Literal as L


# dependencies
from typespecs.typing import (
    get_annotation,
    get_metadata,
    get_subannotations,
    has_metadata,
    is_literal,
)


def test_get_annotation() -> None:
    assert get_annotation(int) == int
    assert get_annotation(Ann[int, 0]) == int
    assert get_annotation(Ann[int, 0], recursive=True) == int
    assert get_annotation(list[Ann[int, 0]]) == list[Ann[int, 0]]
    assert get_annotation(list[Ann[int, 0]], recursive=True) == list[int]


def test_get_metadata() -> None:
    assert get_metadata(int) == []
    assert get_metadata(Ann[int, 0]) == [0]


def test_get_subannotations() -> None:
    assert get_subannotations(int) == []
    assert get_subannotations(L[0]) == []
    assert get_subannotations(str | int) == [str, int]
    assert get_subannotations(Ann[str | int, 0]) == [str, int]


def test_has_metadata() -> None:
    assert has_metadata(Ann[int, 0])
    assert not has_metadata(int)


def test_is_literal() -> None:
    assert is_literal(L[0])
    assert not is_literal(int)
