'Module for a priced item.'
import abc
from decimal import Decimal
from functools import total_ordering

def default_to_self(attribute_name):

    def __post_init__(self):
        if getattr(self, attribute_name) is None:
            setattr(self, attribute_name, self)

    def decorator(cls):
        cls.__post_init__ = __post_init__
        return cls
    return decorator

class PricedObject(abc.ABC):

    @abc.abstractmethod
    def formatted_price(self):
        ...

@default_to_self('parent')
@total_ordering
class Item(PricedObject):
    """Priced item."""
    __slots__ = ('name', 'price', 'parent')
    __match_args__ = ('name', 'price', 'parent')

    def __init__(self, *, name: str, price: Decimal, parent: 'Item'=None) -> None:
        self.name = name
        self.price = price
        self.parent = parent

    def __eq__(self, other):
        if not isinstance(other, Item):
            return NotImplemented
        return (self.name, self.price, self.parent) == (other.name, other.price, other.parent)

    def __lt__(self, other):
        if not isinstance(other, Item):
            return NotImplemented
        return (self.name, self.price, self.parent) < (other.name, other.price, other.parent)

    def __repr__(self):
        items = [f'name={self.name!r}', f'price={self.price!r}']
        if self.parent is not self:
            items.append(f'parent={self.parent!r}')
        return f"Item({', '.join(items)})"

    def formatted_price(self):
        return f'${self.price:.2f}'

    def price_in_cents(self):
        return self.price * 100
