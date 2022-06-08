import dataclasses
from decimal import Decimal
import typing


def default_slugify(name):
    return name.lower().replace(" ", "-")


@dataclasses.dataclass(frozen=True, match_args=False)
class Item:
    name: str
    price: Decimal = Decimal(0)
    _: dataclasses.KW_ONLY
    slug: str = dataclasses.field(init=False, compare=False)
    slugify: dataclasses.InitVar[typing.Callable] = default_slugify

    def __post_init__(self, slugify):
        object.__setattr__(self, "slug", slugify(self.name))
