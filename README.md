# Typespecs

[![Release](https://img.shields.io/pypi/v/typespecs?label=Release&color=cornflowerblue&style=flat-square)](https://pypi.org/project/typespecs/)
[![Python](https://img.shields.io/pypi/pyversions/typespecs?label=Python&color=cornflowerblue&style=flat-square)](https://pypi.org/project/typespecs/)
[![Downloads](https://img.shields.io/pypi/dm/typespecs?label=Downloads&color=cornflowerblue&style=flat-square)](https://pepy.tech/project/typespecs)
[![DOI](https://img.shields.io/badge/DOI-10.5281/zenodo.17681195-cornflowerblue?style=flat-square)](https://doi.org/10.5281/zenodo.17681195)
[![Tests](https://img.shields.io/github/actions/workflow/status/astropenguin/typespecs/tests.yaml?label=Tests&style=flat-square)](https://github.com/astropenguin/typespecs/actions)

Data specifications via type hints

## Overview

**Typespecs** is a lightweight Python library that leverages [`typing.Annotated`](https://docs.python.org/3.14/library/typing.html#typing.Annotated) to manage metadata (category, description, units, ...) within the type hints of your data structures.
It offers a dedicated read-only dictionary called a **type specification** to attach your metadata to your type hints.
This approach keeps your code clean and seamlessly coexists with other `Annotated`-based libraries such as [Pydantic](https://pydantic.dev/).
Finally, the attached metadata can be extracted and aggregated into a [`pandas.DataFrame`](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html) object called a **specification DataFrame**, making it easier to manage it using the rich PyData ecosystem.

## Installation

```bash
pip install typespecs
```

## Basic Usage

You can create and attach a type specification, [`typespecs.Spec(key=value, ...)`](https://astropenguin.github.io/typespecs/_apidoc/typespecs.html#typespecs.Spec), to a type hint of your data structure such as [Python's Data Classes](https://docs.python.org/3.14/library/dataclasses.html) and [Pydantic models](https://pydantic.dev/docs/validation/latest/concepts/models/).
The `Spec` object acts as a read-only dictionary, ensuring your metadata remains immutable and safe from runtime modifications.
Once your data structure is defined, use [`typespecs.from_annotated(obj)`](https://astropenguin.github.io/typespecs/_apidoc/typespecs.html#typespecs.from_annotated) to extract and aggregate the attached metadata into a specification DataFrame.
By default, the actual data and the metadata-stripped type hints will also be stored in the `data` and `type` columns, respectively (you can control this behavior using the `data` and `type` parameters in `from_annotated`).

```python
import typespecs as ts
from dataclasses import dataclass
from typing import Annotated as Ann, ClassVar, TypeVar


@dataclass
class Weather:
    temp: Ann[list[float], ts.Spec(category="data", name="Temperature", units="K")]
    wind: Ann[list[float], ts.Spec(category="data", name="Wind speed", units="m/s")]
    loc: Ann[str, ts.Spec(category="info", name="Observed location")]


weather = Weather([273.15, 280.15], [5.0, 10.0], "Tokyo")
specs = ts.from_annotated(weather)
print(specs)
```
```
      category              data               name           type  units
temp      data  [273.15, 280.15]        Temperature    list[float]      K
wind      data       [5.0, 10.0]         Wind speed    list[float]    m/s
loc       info             Tokyo  Observed location  <class 'str'>   <NA>
```

You can attach multiple `Spec` objects to a single type hint.
If metadata conflicts between them, the last one will take precedence (you can control this behavior using the `conflict` parameters in `from_annotated`; see also [Handling Metadata Conflicts](#handling-metadata-conflicts)).

```python
Temp = Ann[list[float], ts.Spec(category="data", name="Temperature")]
Wind = Ann[list[float], ts.Spec(category="data", name="Wind speed")]
Loc = Ann[str, ts.Spec(category="info", name="Observed Location")]


@dataclass
class Weather:
    temp: Ann[Temp, ts.Spec(units="K")]
    wind: Ann[Wind, ts.Spec(units="m/s")]
    loc: Ann[Loc, ts.Spec(name="City")]


weather = Weather([273.15, 280.15], [5.0, 10.0], "Tokyo")
specs = ts.from_annotated(weather)
print(specs)
```
```
      category              data         name           type  units
temp      data  [273.15, 280.15]  Temperature    list[float]      K
wind      data       [5.0, 10.0]   Wind speed    list[float]    m/s
loc       info             Tokyo         City  <class 'str'>   <NA>
```

## Advanced Usage

### Handling Nested Types

Typespecs simplifies working with nested types.
By default, the metadata attached to nested types will be merged into a single parent row.

```python
Float = Ann[float, ts.Spec(dtype="f8")]


@dataclass
class Weather:
    temp: Ann[list[Float], ts.Spec(category="data", name="Temperature", units="K")]
    wind: Ann[list[Float], ts.Spec(category="data", name="Wind speed", units="m/s")]
    loc: Ann[str, ts.Spec(category="info", name="Observed location")]


weather = Weather([273.15, 280.15], [5.0, 10.0], "Tokyo")
specs = ts.from_annotated(weather)
print(specs)
```
```
      category              data  dtype               name           type  units
temp      data  [273.15, 280.15]     f8        Temperature    list[float]      K
wind      data       [5.0, 10.0]     f8         Wind speed    list[float]    m/s
loc       info             Tokyo   <NA>  Observed location  <class 'str'>   <NA>
```

You can disable this merging behavior using `merge=False` in `from_annotated`.

```python
specs = ts.from_annotated(weather, merge=False)
print(specs)
```
```
        category              data  dtype               name             type  units
temp        data  [273.15, 280.15]   <NA>        Temperature      list[float]      K
temp/0      <NA>              <NA>     f8               <NA>  <class 'float'>   <NA>
wind        data       [5.0, 10.0]   <NA>         Wind speed      list[float]    m/s
wind/0      <NA>              <NA>     f8               <NA>  <class 'float'>   <NA>
loc         info             Tokyo   <NA>  Observed location    <class 'str'>   <NA>
```

Finally, you can include the nested type itself as part of the metadata using the special `typespecs.ITSELF` object.
This is useful when you want to handle the inner type alongside other metadata within the specification DataFrame.

```python
Dtype = Ann[TypeVar("T"), ts.Spec(dtype=ts.ITSELF)]


@dataclass
class Weather:
    temp: Ann[list[Dtype[float]], ts.Spec(category="data", name="Temperature", units="K")]
    wind: Ann[list[Dtype[float]], ts.Spec(category="data", name="Wind speed", units="m/s")]
    loc: Ann[str, ts.Spec(category="info", name="Observed location")]


weather = Weather([273.15, 280.15], [5.0, 10.0], "Tokyo")
specs = ts.from_annotated(weather)
print(specs)
```
```
      category              data            dtype               name           type  units
temp      data  [273.15, 280.15]  <class 'float'>        Temperature    list[float]      K
wind      data       [5.0, 10.0]  <class 'float'>         Wind speed    list[float]    m/s
loc       info             Tokyo             <NA>  Observed location  <class 'str'>   <NA>
```

### Handling Missing Values

By default, missing metadata is filled with `pandas.NA` in a specification DataFrame.
You can pass custom fallback values by using the `default` parameter in `from_annotated`.

```python
specs = ts.from_annotated(weather, default={"dtype": None, "units": "1"})
print(specs)
```
```
      category              data            dtype               name           type  units
temp      data  [273.15, 280.15]  <class 'float'>        Temperature    list[float]      K
wind      data       [5.0, 10.0]  <class 'float'>         Wind speed    list[float]    m/s
loc       info             Tokyo             None  Observed location  <class 'str'>      1
```

### Handling Metadata Conflicts

When multiple `Spec` objects define the same key (either stacked on a single type hint or across nested types), the default behavior is to override the older value with the newer one.
You can customize this conflict resolution strategy using the `conflict` parameter in `from_annotated`.
For example, passing `"update"` instead of `"override"` allows you to cleanly merge dictionary-like metadata.
You can also pass a custom callable to handle more complex conflict resolutions.

```python
Temp = Ann[list[float], ts.Spec(attrs={"sensor": "A", "status": "active"})]
Wind = Ann[list[float], ts.Spec(attrs={"sensor": "A", "status": "active"})]


@dataclass
class Weather:
    temp: Ann[Temp, ts.Spec(attrs={"sensor": "B"})]
    wind: Ann[Wind, ts.Spec(attrs={"sensor": "B"})]


weather = Weather([273.15, 280.15], [5.0, 10.0])
specs = ts.from_annotated(weather)
print(specs)
```
```
                attrs              data         type
temp  {'sensor': 'B'}  [273.15, 280.15]  list[float]
wind  {'sensor': 'B'}       [5.0, 10.0]  list[float]
```
```python
specs = ts.from_annotated(weather, conflict={"attrs": "update"})
print(specs)
```
```
                                    attrs              data         type
temp  {'sensor': 'B', 'status': 'active'}  [273.15, 280.15]  list[float]
wind  {'sensor': 'B', 'status': 'active'}       [5.0, 10.0]  list[float]
```

### Handling Type Hint(s) Directly

You can create a specification DataFrame from type hint(s) using [`typespecs.from_annotation`](https://astropenguin.github.io/typespecs/_apidoc/typespecs.html#typespecs.from_annotation) and [`typespecs.from_annotations`](https://astropenguin.github.io/typespecs/_apidoc/typespecs.html#typespecs.from_annotations).
This is useful when you want to directly handle type hints without defining them within a data structure.

```python
annotations = {
      "temp": Ann[list[Dtype[float]], ts.Spec(category="data", name="Temperature", units="K")],
      "wind": Ann[list[Dtype[float]], ts.Spec(category="data", name="Wind speed", units="m/s")],
      "loc": Ann[str, ts.Spec(category="info", name="Observed location")],
}
specs = ts.from_annotations(annotations)
print(specs)
```
```
      category            dtype               name           type  units
temp      data  <class 'float'>        Temperature    list[float]      K
wind      data  <class 'float'>         Wind speed    list[float]    m/s
loc       info             <NA>  Observed location  <class 'str'>   <NA>
```
```python
specs = ts.from_annotation(annotations["temp"])
print(specs)
```
```
      category            dtype         name         type  units
root      data  <class 'float'>  Temperature  list[float]      K
```

### Configuration for Typespecs

You can define configuration settings directly on an object (or class) to take precedence over the behavior of `from_annotated`.
This is particularly useful when using wrapper libraries where you cannot pass parameters to `from_annotated` directly.
To do this, add the `__typespecs_config__` attribute and assign a dictionary of your settings.
You can optionally type-hint it with [`typespecs.Config`](https://astropenguin.github.io/typespecs/_apidoc/typespecs.html#typespecs.Config) to benefit from static type checking.

```python
Temp = Ann[list[float], ts.Spec(attrs={"sensor": "A", "status": "active"})]
Wind = Ann[list[float], ts.Spec(attrs={"sensor": "A", "status": "active"})]


@dataclass
class Weather:
    __typespecs_config__: ClassVar[ts.Config] = {"conflict": {"attrs": "update"}}

    temp: Ann[Temp, ts.Spec(attrs={"sensor": "B"})]
    wind: Ann[Wind, ts.Spec(attrs={"sensor": "B"})]


weather = Weather([273.15, 280.15], [5.0, 10.0])
specs = ts.from_annotated(weather)
print(specs)
```
```
                                    attrs              data         type
temp  {'sensor': 'B', 'status': 'active'}  [273.15, 280.15]  list[float]
wind  {'sensor': 'B', 'status': 'active'}       [5.0, 10.0]  list[float]
```
