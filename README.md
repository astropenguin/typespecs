# typespecs
Data specifications by type hints

## Examples

```python
from dataclasses import dataclass
from typespecs import Attr, from_dataclass
from typing import Annotated


@dataclass
class Weather:
    temp: Annotated[
        list[float],
        Attr("category", "data"),
        Attr("name", "Temperature"),
        Attr("units", "K"),
    ]
    wind: Annotated[
        list[float],
        Attr("category", "data"),
        Attr("name", "Wind speed"),
        Attr("units", "m/s"),
    ]
    loc: Annotated[
        str,
        Attr("category", "meta"),
        Attr("name", "Observed location"),
    ]


weather = Weather([273.15, 280.15], [5.0, 10.0], "Tokyo")
print(from_dataclass(weather))
```
```
      category               name units              data           type
index
temp      data        Temperature     K  [273.15, 280.15]    list[float]
wind      data         Wind speed   m/s       [5.0, 10.0]    list[float]
loc       meta  Observed location  <NA>             Tokyo  <class 'str'>
```
