from decimal import Decimal
import typing

def default_slugify(name):
    return name.lower().replace(' ', '-')

class Item:

    def __init__(self, name: str, price: Decimal=Decimal(0), *, slugify: typing.Callable=default_slugify) -> None:
        object.__setattr__(self, 'name', name)
        object.__setattr__(self, 'price', price)
        object.__setattr__(self, 'slug', slugify(self.name))

    def __repr__(self):
        cls = type(self).__name__
        return f'{cls}(name={self.name!r}, price={self.price!r}, slug={self.slug!r})'

    def __eq__(self, other):
        if not isinstance(other, Item):
            return NotImplemented
        return (self.name, self.price) == (other.name, other.price)

    def __hash__(self):
        return hash((self.name, self.price))

    def __setattr__(self, name, value):
        raise AttributeError(f"Can't set attribute {name!r}")

    def __delattr__(self, name):
        raise AttributeError(f"Can't delete attribute {name!r}")
