from random import randint, random
from types import Any

class Base:
    __match_args__ = ('x', 'y')

    def __init__(self, x: Any=None, y: int=0) -> None:
        if x is None:
            x = randint(0, 20)
        self.x = x
        self.y = y

    def __repr__(self):
        cls = type(self).__name__
        return f'{cls}(x={self.x!r}, y={self.y!r})'

    def __eq__(self, other):
        if not isinstance(other, Base):
            return NotImplemented
        return (self.x, self.y) == (other.x, other.y)

class C(Base):
    __match_args__ = ('x', 'y', 'z')

    def __init__(self, x: int=15, y: int=0, z: int=10) -> None:
        self.x = x
        self.y = y
        self.z = z

    def __repr__(self):
        cls = type(self).__name__
        return f'{cls}(x={self.x!r}, y={self.y!r}, z={self.z!r})'

    def __eq__(self, other):
        if not isinstance(other, C):
            return NotImplemented
        return (self.x, self.y, self.z) == (other.x, other.y, other.z)

class Base:
    __match_args__ = ('x', 'y', 'w')

    def __init__(self, x: Any=15.0, *, y: int=None, w: int=1) -> None:
        if y is None:
            y = random()
        self.x = x
        self.y = y
        self.w = w

    def __repr__(self):
        cls = type(self).__name__
        return f'{cls}(x={self.x!r}, y={self.y!r}, w={self.w!r})'

    def __eq__(self, other):
        if not isinstance(other, Base):
            return NotImplemented
        return (self.x, self.y, self.w) == (other.x, other.y, other.w)

class D(Base):
    __match_args__ = ('x', 'y', 'w', 'z', 't')

    def __init__(self, x: Any=15.0, z: int=10, *, y: int=None, w: int=1, t: int=0) -> None:
        if y is None:
            y = random()
        self.x = x
        self.y = y
        self.w = w
        self.z = z
        self.t = t

    def __repr__(self):
        cls = type(self).__name__
        return f'{cls}(x={self.x!r}, y={self.y!r}, w={self.w!r}, z={self.z!r}, t={self.t!r})'

    def __eq__(self, other):
        if not isinstance(other, D):
            return NotImplemented
        return (self.x, self.y, self.w, self.z, self.t) == (other.x, other.y, other.w, other.z, other.t)
