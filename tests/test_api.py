# standard library
from dataclasses import dataclass
from typing import Annotated as Ann

# dependencies
from pandas import NA, DataFrame
from pandas.testing import assert_frame_equal
from typespecs import (
    ITSELF,
    ItselfType,
    Spec,
    from_annotated,
    from_annotation,
    from_annotations,
)


def test_itself() -> None:
    assert ItselfType() == ItselfType()
    assert ItselfType() == ITSELF
    assert ItselfType() is not ItselfType()
    assert ItselfType() is not ITSELF


def test_from_annotated() -> None:
    @dataclass
    class Weather:
        temp: Ann[
            list[Ann[float, Spec(dtype=ITSELF)]],
            Spec(name="Temperature", units="degC"),
        ]
        wind: Ann[
            list[Ann[float, Spec(dtype=ITSELF)]],
            Spec(name="Wind speed", units="m/s"),
        ]

    obj = Weather(temp=[20.0, 25.0], wind=[3.0, 5.0])
    specs = DataFrame(
        data={
            "data": [[20.0, 25.0], NA, [3.0, 5.0], NA],
            "dtype": [NA, float, NA, float],
            "name": ["Temperature", NA, "Wind speed", NA],
            "type": [list[float], float, list[float], float],
            "units": ["degC", NA, "m/s", NA],
        },
        index=["temp", "temp/0", "wind", "wind/0"],
        dtype=object,
    )

    assert_frame_equal(
        from_annotated(obj, default=NA, merge=False),
        specs,
        check_exact=True,
    )


def test_from_annotated_with_default() -> None:
    @dataclass
    class Weather:
        temp: Ann[
            list[Ann[float, Spec(dtype=ITSELF)]],
            Spec(name="Temperature", units="degC"),
        ]
        wind: Ann[
            list[Ann[float, Spec(dtype=ITSELF)]],
            Spec(name="Wind speed", units="m/s"),
        ]

    obj = Weather(temp=[20.0, 25.0], wind=[3.0, 5.0])
    specs = DataFrame(
        data={
            "data": [[20.0, 25.0], None, [3.0, 5.0], None],
            "dtype": [None, float, None, float],
            "name": ["Temperature", None, "Wind speed", None],
            "type": [list[float], float, list[float], float],
            "units": ["degC", None, "m/s", None],
        },
        index=["temp", "temp/0", "wind", "wind/0"],
        dtype=object,
    )

    assert_frame_equal(
        from_annotated(obj, default=None, merge=False),
        specs,
        check_exact=True,
    )


def test_from_annotated_with_merge() -> None:
    @dataclass
    class Weather:
        temp: Ann[
            list[Ann[float, Spec(dtype=ITSELF)]],
            Spec(name="Temperature", units="degC"),
        ]
        wind: Ann[
            list[Ann[float, Spec(dtype=ITSELF)]],
            Spec(name="Wind speed", units="m/s"),
        ]

    obj = Weather(temp=[20.0, 25.0], wind=[3.0, 5.0])
    specs = DataFrame(
        data={
            "data": [[20.0, 25.0], [3.0, 5.0]],
            "dtype": [float, float],
            "name": ["Temperature", "Wind speed"],
            "type": [list[float], list[float]],
            "units": ["degC", "m/s"],
        },
        index=["temp", "wind"],
        dtype=object,
    )

    assert_frame_equal(
        from_annotated(obj, default=NA, merge=True),
        specs,
        check_exact=True,
    )


def test_from_annotation() -> None:
    obj = Ann[
        list[Ann[int, Spec(dtype=ITSELF)]],
        Spec(category="data"),
    ]
    specs = DataFrame(
        data={
            "category": ["data", NA],
            "dtype": [NA, int],
            "type": [list[int], int],
        },
        index=["root", "root/0"],
        dtype=object,
    )

    assert_frame_equal(
        from_annotation(obj, default=NA, merge=False),
        specs,
        check_exact=True,
    )


def test_from_annotation_with_default() -> None:
    obj = Ann[
        list[Ann[int, Spec(dtype=ITSELF)]],
        Spec(category="data"),
    ]
    specs = DataFrame(
        data={
            "category": ["data", None],
            "dtype": [None, int],
            "type": [list[int], int],
        },
        index=["root", "root/0"],
        dtype=object,
    )

    assert_frame_equal(
        from_annotation(obj, default=None, merge=False),
        specs,
        check_exact=True,
    )


def test_from_annotation_with_merge() -> None:
    obj = Ann[
        list[Ann[int, Spec(dtype=ITSELF)]],
        Spec(category="data"),
    ]
    specs = DataFrame(
        data={
            "category": ["data"],
            "dtype": [int],
            "type": [list[int]],
        },
        index=["root"],
        dtype=object,
    )

    assert_frame_equal(
        from_annotation(obj, default=NA, merge=True),
        specs,
        check_exact=True,
    )


def test_from_annotations() -> None:
    obj = {
        "temp": Ann[
            list[Ann[float, Spec(dtype=ITSELF)]],
            Spec(name="Temperature", units="degC"),
        ],
        "wind": Ann[
            list[Ann[float, Spec(dtype=ITSELF)]],
            Spec(name="Wind speed", units="m/s"),
        ],
    }

    specs = DataFrame(
        data={
            "dtype": [NA, float, NA, float],
            "name": ["Temperature", NA, "Wind speed", NA],
            "type": [list[float], float, list[float], float],
            "units": ["degC", NA, "m/s", NA],
        },
        index=["temp", "temp/0", "wind", "wind/0"],
        dtype=object,
    )

    assert_frame_equal(
        from_annotations(obj, default=NA, merge=False),
        specs,
        check_exact=True,
    )


def test_from_annotations_with_default() -> None:
    obj = {
        "temp": Ann[
            list[Ann[float, Spec(dtype=ITSELF)]],
            Spec(name="Temperature", units="degC"),
        ],
        "wind": Ann[
            list[Ann[float, Spec(dtype=ITSELF)]],
            Spec(name="Wind speed", units="m/s"),
        ],
    }

    specs = DataFrame(
        data={
            "dtype": [None, float, None, float],
            "name": ["Temperature", None, "Wind speed", None],
            "type": [list[float], float, list[float], float],
            "units": ["degC", None, "m/s", None],
        },
        index=["temp", "temp/0", "wind", "wind/0"],
        dtype=object,
    )

    assert_frame_equal(
        from_annotations(obj, default=None, merge=False),
        specs,
        check_exact=True,
    )


def test_from_annotations_with_merge() -> None:
    obj = {
        "temp": Ann[
            list[Ann[float, Spec(dtype=ITSELF)]],
            Spec(name="Temperature", units="degC"),
        ],
        "wind": Ann[
            list[Ann[float, Spec(dtype=ITSELF)]],
            Spec(name="Wind speed", units="m/s"),
        ],
    }

    specs = DataFrame(
        data={
            "dtype": [float, float],
            "name": ["Temperature", "Wind speed"],
            "type": [list[float], list[float]],
            "units": ["degC", "m/s"],
        },
        index=["temp", "wind"],
        dtype=object,
    )

    assert_frame_equal(
        from_annotations(obj, default=NA, merge=True),
        specs,
        check_exact=True,
    )
