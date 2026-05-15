# standard library
from dataclasses import dataclass
from typing import Annotated as Ann

# dependencies
import typespecs as ts
import pandas as pd
from pandas.testing import assert_frame_equal


@dataclass
class Weather:
    temp: Ann[
        list[Ann[float, ts.Spec(dtype=ts.ITSELF, meta={"a": 2, "b": 2, "c": 2})]],
        ts.Spec(name="Temperature", units="degC", meta={"a": 1, "b": 1}),
        ts.Spec(meta={"a": 0}),
    ]
    wind: Ann[
        list[Ann[float, ts.Spec(dtype=ts.ITSELF, meta={"a": 2, "b": 2, "c": 2})]],
        ts.Spec(name="Wind speed", units="m/s", meta={"a": 1, "b": 1}),
        ts.Spec(meta={"a": 0}),
    ]


ANNOTATION = Ann[
    list[Ann[int, ts.Spec(dtype=ts.ITSELF, meta={"a": 2, "b": 2, "c": 2})]],
    ts.Spec(category="data", meta={"a": 1, "b": 1}),
    ts.Spec(meta={"a": 0}),
]
ANNOTATIONS = {
    "temp": Ann[
        list[Ann[float, ts.Spec(dtype=ts.ITSELF, meta={"a": 2, "b": 2, "c": 2})]],
        ts.Spec(name="Temperature", units="degC", meta={"a": 1, "b": 1}),
        ts.Spec(meta={"a": 0}),
    ],
    "wind": Ann[
        list[Ann[float, ts.Spec(dtype=ts.ITSELF, meta={"a": 2, "b": 2, "c": 2})]],
        ts.Spec(name="Wind speed", units="m/s", meta={"a": 1, "b": 1}),
        ts.Spec(meta={"a": 0}),
    ],
}


def test_itself() -> None:
    assert ts.ItselfType() == ts.ItselfType()
    assert ts.ItselfType() == ts.ITSELF
    assert ts.ItselfType() is not ts.ItselfType()
    assert ts.ItselfType() is not ts.ITSELF


def test_from_annotated() -> None:
    obj = Weather(temp=[20.0, 25.0], wind=[3.0, 5.0])
    specs = pd.DataFrame(
        data={
            "data": [[20.0, 25.0], pd.NA, [3.0, 5.0], pd.NA],
            "dtype": [pd.NA, float, pd.NA, float],
            "meta": [
                {"a": 0},
                {"a": 2, "b": 2, "c": 2},
                {"a": 0},
                {"a": 2, "b": 2, "c": 2},
            ],
            "name": ["Temperature", pd.NA, "Wind speed", pd.NA],
            "type": [list[float], float, list[float], float],
            "units": ["degC", pd.NA, "m/s", pd.NA],
        },
        index=["temp", "temp/0", "wind", "wind/0"],
        dtype=object,
    )

    assert_frame_equal(
        ts.from_annotated(
            obj,
            conflict="override",
            default=pd.NA,
            merge=False,
        ),
        specs,
        check_exact=True,
    )


def test_from_annotated_with_default() -> None:
    obj = Weather(temp=[20.0, 25.0], wind=[3.0, 5.0])
    specs = pd.DataFrame(
        data={
            "data": [[20.0, 25.0], None, [3.0, 5.0], None],
            "dtype": [None, float, None, float],
            "meta": [
                {"a": 0},
                {"a": 2, "b": 2, "c": 2},
                {"a": 0},
                {"a": 2, "b": 2, "c": 2},
            ],
            "name": ["Temperature", None, "Wind speed", None],
            "type": [list[float], float, list[float], float],
            "units": ["degC", None, "m/s", None],
        },
        index=["temp", "temp/0", "wind", "wind/0"],
        dtype=object,
    )

    assert_frame_equal(
        ts.from_annotated(
            obj,
            conflict="override",
            default=None,
            merge=False,
        ),
        specs,
        check_exact=True,
    )


def test_from_annotated_with_merge() -> None:
    obj = Weather(temp=[20.0, 25.0], wind=[3.0, 5.0])
    specs = pd.DataFrame(
        data={
            "data": [[20.0, 25.0], [3.0, 5.0]],
            "dtype": [float, float],
            "meta": [{"a": 0}, {"a": 0}],
            "name": ["Temperature", "Wind speed"],
            "type": [list[float], list[float]],
            "units": ["degC", "m/s"],
        },
        index=["temp", "wind"],
        dtype=object,
    )

    assert_frame_equal(
        ts.from_annotated(
            obj,
            conflict="override",
            default=pd.NA,
            merge=True,
        ),
        specs,
        check_exact=True,
    )


def test_from_annotated_with_conflict() -> None:
    obj = Weather(temp=[20.0, 25.0], wind=[3.0, 5.0])
    specs = pd.DataFrame(
        data={
            "data": [[20.0, 25.0], [3.0, 5.0]],
            "dtype": [float, float],
            "meta": [{"a": 0, "b": 1, "c": 2}, {"a": 0, "b": 1, "c": 2}],
            "name": ["Temperature", "Wind speed"],
            "type": [list[float], list[float]],
            "units": ["degC", "m/s"],
        },
        index=["temp", "wind"],
        dtype=object,
    )

    assert_frame_equal(
        ts.from_annotated(
            obj,
            conflict={"meta": "update"},
            default=pd.NA,
            merge=True,
        ),
        specs,
        check_exact=True,
    )


def test_from_annotation() -> None:
    specs = pd.DataFrame(
        data={
            "category": ["data", pd.NA],
            "dtype": [pd.NA, int],
            "meta": [{"a": 0}, {"a": 2, "b": 2, "c": 2}],
            "type": [list[int], int],
        },
        index=["root", "root/0"],
        dtype=object,
    )

    assert_frame_equal(
        ts.from_annotation(
            ANNOTATION,
            conflict="override",
            default=pd.NA,
            merge=False,
        ),
        specs,
        check_exact=True,
    )


def test_from_annotation_with_default() -> None:
    specs = pd.DataFrame(
        data={
            "category": ["data", None],
            "dtype": [None, int],
            "meta": [{"a": 0}, {"a": 2, "b": 2, "c": 2}],
            "type": [list[int], int],
        },
        index=["root", "root/0"],
        dtype=object,
    )

    assert_frame_equal(
        ts.from_annotation(
            ANNOTATION,
            conflict="override",
            default=None,
            merge=False,
        ),
        specs,
        check_exact=True,
    )


def test_from_annotation_with_merge() -> None:
    specs = pd.DataFrame(
        data={
            "category": ["data"],
            "dtype": [int],
            "meta": [{"a": 0}],
            "type": [list[int]],
        },
        index=["root"],
        dtype=object,
    )

    assert_frame_equal(
        ts.from_annotation(
            ANNOTATION,
            conflict="override",
            default=pd.NA,
            merge=True,
        ),
        specs,
        check_exact=True,
    )


def test_from_annotation_with_conflict() -> None:
    specs = pd.DataFrame(
        data={
            "category": ["data"],
            "dtype": [int],
            "meta": [{"a": 0, "b": 1, "c": 2}],
            "type": [list[int]],
        },
        index=["root"],
        dtype=object,
    )

    assert_frame_equal(
        ts.from_annotation(
            ANNOTATION,
            conflict={"meta": "update"},
            default=pd.NA,
            merge=True,
        ),
        specs,
        check_exact=True,
    )


def test_from_annotations() -> None:
    specs = pd.DataFrame(
        data={
            "dtype": [pd.NA, float, pd.NA, float],
            "meta": [
                {"a": 0},
                {"a": 2, "b": 2, "c": 2},
                {"a": 0},
                {"a": 2, "b": 2, "c": 2},
            ],
            "name": ["Temperature", pd.NA, "Wind speed", pd.NA],
            "type": [list[float], float, list[float], float],
            "units": ["degC", pd.NA, "m/s", pd.NA],
        },
        index=["temp", "temp/0", "wind", "wind/0"],
        dtype=object,
    )

    assert_frame_equal(
        ts.from_annotations(
            ANNOTATIONS,
            conflict="override",
            default=pd.NA,
            merge=False,
        ),
        specs,
        check_exact=True,
    )


def test_from_annotations_with_default() -> None:
    specs = pd.DataFrame(
        data={
            "dtype": [None, float, None, float],
            "meta": [
                {"a": 0},
                {"a": 2, "b": 2, "c": 2},
                {"a": 0},
                {"a": 2, "b": 2, "c": 2},
            ],
            "name": ["Temperature", None, "Wind speed", None],
            "type": [list[float], float, list[float], float],
            "units": ["degC", None, "m/s", None],
        },
        index=["temp", "temp/0", "wind", "wind/0"],
        dtype=object,
    )

    assert_frame_equal(
        ts.from_annotations(
            ANNOTATIONS,
            conflict="override",
            default=None,
            merge=False,
        ),
        specs,
        check_exact=True,
    )


def test_from_annotations_with_merge() -> None:
    specs = pd.DataFrame(
        data={
            "dtype": [float, float],
            "meta": [{"a": 0}, {"a": 0}],
            "name": ["Temperature", "Wind speed"],
            "type": [list[float], list[float]],
            "units": ["degC", "m/s"],
        },
        index=["temp", "wind"],
        dtype=object,
    )

    assert_frame_equal(
        ts.from_annotations(
            ANNOTATIONS,
            conflict="override",
            default=pd.NA,
            merge=True,
        ),
        specs,
        check_exact=True,
    )


def test_from_annotations_with_conflict() -> None:
    specs = pd.DataFrame(
        data={
            "dtype": [float, float],
            "meta": [{"a": 0, "b": 1, "c": 2}, {"a": 0, "b": 1, "c": 2}],
            "name": ["Temperature", "Wind speed"],
            "type": [list[float], list[float]],
            "units": ["degC", "m/s"],
        },
        index=["temp", "wind"],
        dtype=object,
    )

    assert_frame_equal(
        ts.from_annotations(
            ANNOTATIONS,
            conflict={"meta": "update"},
            default=pd.NA,
            merge=True,
        ),
        specs,
        check_exact=True,
    )
