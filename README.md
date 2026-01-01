# typespecs

[![Release](https://img.shields.io/pypi/v/typespecs?label=Release&color=cornflowerblue&style=flat-square)](https://pypi.org/project/typespecs/)
[![Python](https://img.shields.io/pypi/pyversions/typespecs?label=Python&color=cornflowerblue&style=flat-square)](https://pypi.org/project/typespecs/)
[![Downloads](https://img.shields.io/pypi/dm/typespecs?label=Downloads&color=cornflowerblue&style=flat-square)](https://pepy.tech/project/typespecs)
[![DOI](https://img.shields.io/badge/DOI-10.5281/zenodo.17681195-cornflowerblue?style=flat-square)](https://doi.org/10.5281/zenodo.17681195)
[![Tests](https://img.shields.io/github/actions/workflow/status/astropenguin/typespecs/tests.yaml?label=Tests&style=flat-square)](https://github.com/astropenguin/typespecs/actions)

Data specifications by type hints

## Installation

```bash
pip install typespecs
```

## Basic Usage

```python
from dataclasses import dataclass
from typespecs import ITSELF, Spec, from_annotated
from typing import Annotated as Ann


@dataclass
class Weather:
    temp: Ann[list[float], Spec(category="data", name="Temperature", units="K")]
    wind: Ann[list[float], Spec(category="data", name="Wind speed", units="m/s")]
    loc: Ann[str, Spec(category="metadata", name="Observed location")]


weather = Weather([273.15, 280.15], [5.0, 10.0], "Tokyo")
specs = from_annotated(weather)
print(specs)
```
```
      category              data               name           type units
temp      data  [273.15, 280.15]        Temperature    list[float]     K
wind      data       [5.0, 10.0]         Wind speed    list[float]   m/s
loc   metadata             Tokyo  Observed location  <class 'str'>  <NA>
```

## Advanced Usage

### Handling Sub-annotations

```python
Float = Ann[float, Spec(dtype=ITSELF)]


@dataclass
class Weather:
    temp: Ann[list[Float], Spec(category="data", name="Temperature", units="K")]
    wind: Ann[list[Float], Spec(category="data", name="Wind speed", units="m/s")]
    loc: Ann[str, Spec(category="metadata", name="Observed location")]


weather = Weather([273.15, 280.15], [5.0, 10.0], "Tokyo")
specs = from_annotated(weather)
print(specs)
```
```
      category              data            dtype               name           type units
temp      data  [273.15, 280.15]  <class 'float'>        Temperature    list[float]     K
wind      data       [5.0, 10.0]  <class 'float'>         Wind speed    list[float]   m/s
loc   metadata             Tokyo             <NA>  Observed location  <class 'str'>  <NA>
```

### Handling Missing Values

```python
specs = from_annotated(weather, default=None)
print(specs)
```
```
      category              data            dtype               name           type units
temp      data  [273.15, 280.15]  <class 'float'>        Temperature    list[float]     K
wind      data       [5.0, 10.0]  <class 'float'>         Wind speed    list[float]   m/s
loc   metadata             Tokyo             None  Observed location  <class 'str'>  None
```

### Handling Full Specification

```python
specs = from_annotated(weather, merge=False)
print(specs)
```
```
        category              data            dtype               name             type units
temp        data  [273.15, 280.15]             <NA>        Temperature      list[float]     K
temp/0      <NA>              <NA>  <class 'float'>               <NA>  <class 'float'>  <NA>
wind        data       [5.0, 10.0]             <NA>         Wind speed      list[float]   m/s
wind/0      <NA>              <NA>  <class 'float'>               <NA>  <class 'float'>  <NA>
loc     metadata             Tokyo             <NA>  Observed location    <class 'str'>  <NA>
```
