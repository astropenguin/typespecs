# typespecs

[![Release](https://img.shields.io/pypi/v/typespecs?label=Release&color=cornflowerblue&style=flat-square)](https://pypi.org/project/typespecs/)
[![Python](https://img.shields.io/pypi/pyversions/typespecs?label=Python&color=cornflowerblue&style=flat-square)](https://pypi.org/project/typespecs/)
[![Downloads](https://img.shields.io/pypi/dm/typespecs?label=Downloads&color=cornflowerblue&style=flat-square)](https://pepy.tech/project/typespecs)
[![Tests](https://img.shields.io/github/actions/workflow/status/astropenguin/typespecs/tests.yaml?label=Tests&style=flat-square)](https://github.com/astropenguin/typespecs/actions)

Data specifications by type hints

## Examples

```python
from dataclasses import dataclass
from typespecs import Spec, from_dataclass
from typing import Annotated as Ann


@dataclass
class Weather:
    temp: Ann[list[float], Spec(category="data", name="Temperature", units="K")]
    wind: Ann[list[float], Spec(category="data", name="Wind speed", units="m/s")]
    loc: Ann[str, Spec(category="metadata", name="Observed location")]


weather = Weather([273.15, 280.15], [5.0, 10.0], "Tokyo")
specs = from_dataclass(weather)
print(specs)
```
```
      category              data               name           type units
temp      data  [273.15, 280.15]        Temperature    list[float]     K
wind      data       [5.0, 10.0]         Wind speed    list[float]   m/s
loc   metadata             Tokyo  Observed location  <class 'str'>  <NA>
```
