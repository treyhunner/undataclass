class Point:
    """A two-dimensional point."""
    __match_args__ = ('x', 'y')

    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    def __repr__(self):
        cls = type(self).__name__
        return f'{cls}(x={self.x!r}, y={self.y!r})'

    def __eq__(self, other):
        if not isinstance(other, Point):
            return NotImplemented
        return (self.x, self.y) == (other.x, other.y)
