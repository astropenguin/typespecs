# Typespecs

[![Release](https://img.shields.io/pypi/v/typespecs?label=Release&color=cornflowerblue&style=flat-square)](https://pypi.org/project/typespecs/)
[![Python](https://img.shields.io/pypi/pyversions/typespecs?label=Python&color=cornflowerblue&style=flat-square)](https://pypi.org/project/typespecs/)
[![Downloads](https://img.shields.io/pypi/dm/typespecs?label=Downloads&color=cornflowerblue&style=flat-square)](https://pepy.tech/project/typespecs)
[![DOI](https://img.shields.io/badge/DOI-10.5281/zenodo.17681195-cornflowerblue?style=flat-square)](https://doi.org/10.5281/zenodo.17681195)
[![Tests](https://img.shields.io/github/actions/workflow/status/astropenguin/typespecs/tests.yaml?label=Tests&style=flat-square)](https://github.com/astropenguin/typespecs/actions)

Data specifications by type hints

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
Once your data structure is defined, use [`typespecs.from_annotated`](https://astropenguin.github.io/typespecs/_apidoc/typespecs.html#typespecs.from_annotated) to extract and aggregate the attached metadata into a specification DataFrame.
By default, the actual data and the metadata-stripped type hints will also be stored in the `data` and `type` columns, respectively (you can control this behavior using the `data` and `type` parameters in `from_annotated`).
```python
import typespecs as ts
from dataclasses import dataclass
from typing import Annotated as Ann, TypeVar


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
If metadata overlaps between them, the last one will take precedence.
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

### Handling Sub-annotations

Typespecs simplifies working with nested types.
You can easily create reusable type aliases with built-in specifications.
Furthermore, by using the special `typespecs.ITSELF` object, the library dynamically captures the subtype (e.g., `float` in `list[float]`) as one of metadata.

```python
T = TypeVar("T")
Dtype = Ann[T, ts.Spec(dtype=ts.ITSELF)]


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
      category              data            dtype               name           type units
temp      data  [273.15, 280.15]  <class 'float'>        Temperature    list[float]     K
wind      data       [5.0, 10.0]  <class 'float'>         Wind speed    list[float]   m/s
loc       info             Tokyo             <NA>  Observed location  <class 'str'>  <NA>
```

### Handling Missing Values

By default, missing metadata values are filled with `pandas.NA`.
You can override this behavior and specify a custom fallback value by using the `default` parameter in `from_annotated`.

```python
specs = ts.from_annotated(weather, default=None)
print(specs)
```
```
      category              data            dtype               name           type units
temp      data  [273.15, 280.15]  <class 'float'>        Temperature    list[float]     K
wind      data       [5.0, 10.0]  <class 'float'>         Wind speed    list[float]   m/s
loc       info             Tokyo             None  Observed location  <class 'str'>  None
```

### Handling Full Specification

By default, typespecs neatly merges nested metadata (e.g., `float` in `list[float]`) into a single parent row.
If you need to inspect the exact structural hierarchy of your annotations, set `merge=False` in `from_annotated`.
This unpacks the tree, distinguishing between the parent collection and its elements.

```python
specs = ts.from_annotated(weather, merge=False)
print(specs)
```
```
        category              data            dtype               name             type units
temp        data  [273.15, 280.15]             <NA>        Temperature      list[float]     K
temp/0      <NA>              <NA>  <class 'float'>               <NA>  <class 'float'>  <NA>
wind        data       [5.0, 10.0]             <NA>         Wind speed      list[float]   m/s
wind/0      <NA>              <NA>  <class 'float'>               <NA>  <class 'float'>  <NA>
loc         info             Tokyo             <NA>  Observed location    <class 'str'>  <NA>
```
