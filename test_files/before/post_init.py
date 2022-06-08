import dataclasses
import decimal


@dataclasses.dataclass
class Item:
    name: str
    price: decimal.Decimal

    __slots__ = ("name", "price", "slug")

    def __post_init__(self):
        self.slug = self.name.lower().replace(" ", "-")
