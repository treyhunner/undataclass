from decimal import Decimal
from functools import total_ordering

@total_ordering
class Item:
    __slots__ = ('name', 'price', 'colors')
    __match_args__ = ('name', 'price', 'colors')

    def __init__(self, name: str, price: Decimal=Decimal(0), colors: str=None) -> None:
        if colors is None:
            colors = []
        object.__setattr__(self, 'name', name)
        object.__setattr__(self, 'price', price)
        object.__setattr__(self, 'colors', colors)

    def __repr__(self):
        cls = type(self).__name__
        return f'{cls}(name={self.name!r}, price={self.price!r}, colors={self.colors!r})'

    def __eq__(self, other):
        if not isinstance(other, Item):
            return NotImplemented
        return (self.name, self.price) == (other.name, other.price)

    def __lt__(self, other):
        if not isinstance(other, Item):
            return NotImplemented
        return (self.name, self.price) < (other.name, other.price)

    def __hash__(self):
        return hash((self.name, self.price))

    def __setattr__(self, name, value):
        raise AttributeError(f"Can't set attribute {name!r}")

    def __delattr__(self, name):
        raise AttributeError(f"Can't delete attribute {name!r}")

    def __getstate__(self):
        return (self.name, self.price, self.colors)

    def __setstate__(self, state):
        fields = ('name', 'price', 'colors')
        for (field, value) in zip(fields, state):
            object.__setattr__(self, field, value)
