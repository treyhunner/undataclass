from dataclasses import dataclass, field
from decimal import Decimal


@dataclass(frozen=True, slots=True, order=True)
class Item:
    name: str
    price: Decimal = Decimal(0)
    colors: str = field(default_factory=list)
