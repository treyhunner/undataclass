"""Module for a priced item."""
import abc
from dataclasses import dataclass, field
from decimal import Decimal


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


@dataclass(repr=False, order=True, slots=True, kw_only=True)
@default_to_self("parent")
class Item(PricedObject):

    """Priced item."""

    name: str
    price: Decimal
    parent: 'Item' = field(default=None)

    def __repr__(self):
        items = [f"name={self.name!r}", f"price={self.price!r}"]
        if self.parent is not self:
            items.append(f"parent={self.parent!r}")
        return f"Item({', '.join(items)})"

    def formatted_price(self):
        return f"${self.price:.2f}"

    def price_in_cents(self):
        return self.price*100
