# typespecs
Data specifications by type hints

## Examples

```python
from dataclasses import dataclass
from typespecs import Attrs, from_dataclass
from typing import Annotated as Ann


@dataclass
class Weather:
    temp: Ann[list[float], Attrs(kind="data", name="Temperature", units="K")]
    wind: Ann[list[float], Attrs(kind="data", name="Wind speed", units="m/s")]
    loc: Ann[str, Attrs(kind="meta", name="Observed location")]


weather = Weather([273.15, 280.15], [5.0, 10.0], "Tokyo")
print(from_dataclass(weather))
```
```
       kind               name units              data           type
index
temp   data        Temperature     K  [273.15, 280.15]    list[float]
wind   data         Wind speed   m/s       [5.0, 10.0]    list[float]
loc    meta  Observed location  <NA>             Tokyo  <class 'str'>
```
