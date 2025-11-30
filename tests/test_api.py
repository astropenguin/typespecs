# standard library
from dataclasses import dataclass
from typing import Annotated as Ann


# dependencies
import pandas as pd
from pandas.testing import assert_frame_equal
from typespecs import (
    ITSELF,
    Spec,
    from_annotated,
    from_annotation,
    from_annotations,
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
    specs = pd.DataFrame(
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
        from_annotated(obj, merge=True),
        specs,
        check_exact=True,
    )


def test_from_annotated_without_merge() -> None:
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
    specs = pd.DataFrame(
        data={
            "data": [[20.0, 25.0], pd.NA, [3.0, 5.0], pd.NA],
            "dtype": [pd.NA, float, pd.NA, float],
            "name": ["Temperature", pd.NA, "Wind speed", pd.NA],
            "type": [list[float], float, list[float], float],
            "units": ["degC", pd.NA, "m/s", pd.NA],
        },
        index=["temp", "temp/0", "wind", "wind/0"],
        dtype=object,
    )

    assert_frame_equal(
        from_annotated(obj, merge=False),
        specs,
        check_exact=True,
    )


def test_from_annotation_with_merge() -> None:
    obj = Ann[
        list[Ann[int, Spec(dtype=ITSELF)]],
        Spec(category="data"),
    ]
    specs = pd.DataFrame(
        data={
            "category": ["data"],
            "dtype": [int],
            "type": [list[int]],
        },
        index=["root"],
        dtype=object,
    )

    assert_frame_equal(
        from_annotation(obj, merge=True),
        specs,
        check_exact=True,
    )


def test_from_annotation_without_merge() -> None:
    obj = Ann[
        list[Ann[int, Spec(dtype=ITSELF)]],
        Spec(category="data"),
    ]
    specs = pd.DataFrame(
        data={
            "category": ["data", pd.NA],
            "dtype": [pd.NA, int],
            "type": [list[int], int],
        },
        index=["root", "root/0"],
        dtype=object,
    )

    assert_frame_equal(
        from_annotation(obj, merge=False),
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

    specs = pd.DataFrame(
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
        from_annotations(obj, merge=True),
        specs,
        check_exact=True,
    )


def test_from_annotations_without_merge() -> None:
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

    specs = pd.DataFrame(
        data={
            "dtype": [pd.NA, float, pd.NA, float],
            "name": ["Temperature", pd.NA, "Wind speed", pd.NA],
            "type": [list[float], float, list[float], float],
            "units": ["degC", pd.NA, "m/s", pd.NA],
        },
        index=["temp", "temp/0", "wind", "wind/0"],
        dtype=object,
    )

    assert_frame_equal(
        from_annotations(obj, merge=False),
        specs,
        check_exact=True,
    )
