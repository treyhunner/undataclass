from dataclasses import dataclass, field, KW_ONLY
from random import randint, random
from types import Any


@dataclass
class Base:
    x: Any = field(default_factory=lambda: randint(0, 20))
    y: int = 0


@dataclass
class C(Base):
    z: int = 10
    x: int = 15


@dataclass
class Base:
    x: Any = 15.0
    _: KW_ONLY
    y: int = field(default_factory=random)
    w: int = 1


@dataclass
class D(Base):
    z: int = 10
    t: int = field(kw_only=True, default=0)
