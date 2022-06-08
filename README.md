# undataclass

Turn dataclasses into not-dataclasses


## Usage

Given a `my_module.py` file containing one or more dataclasses:

```python
from dataclasses import dataclass, field
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class Item:
    name: str
    price: Decimal = Decimal(0)
    color: str = field(default_factory=random.choice(("purple", "green")))
```

You can run the `undataclass.py` script against your `my_module.py` file to output a new equivalent module with dataclasses replaced by non-dataclasses:

```bash
$ python3 undataclass.py my_module.py
from decimal import Decimal
import random

class Item:
    __slots__ = ('name', 'price', 'color')
    __match_args__ = ('name', 'price', 'color')

    def __init__(self, name: str, price: Decimal=Decimal(0), color: str=None) -> None:
        if color is None:
            color = random.choice(('purple', 'green'))()
        object.__setattr__(self, 'name', name)
        object.__setattr__(self, 'price', price)
        object.__setattr__(self, 'color', color)

    def __repr__(self):
        cls = type(self).__name__
        return f'{cls}(name={self.name!r}, price={self.price!r}, color={self.color!r})'

    def __eq__(self, other):
        if not isinstance(other, Item):
            return NotImplemented
        return (self.name, self.price, self.color) == (other.name, other.price, other.color)

    def __lt__(self, other):
        if not isinstance(other, Item):
            return NotImplemented
        return (self.name, self.price, self.color) < (other.name, other.price, other.color)

    def __hash__(self):
        return hash((self.name, self.price, self.color))

    def __setattr__(self, name, value):
        raise AttributeError(f"Can't set attribute {name!r}")

    def __delattr__(self, name):
        raise AttributeError(f"Can't delete attribute {name!r}")

    def __getstate__(self):
        return (self.name, self.price, self.color)

    def __setstate__(self, state):
        fields = ('name', 'price', 'color')
        for (field, value) in zip(fields, state):
            object.__setattr__(self, field, value)
```
