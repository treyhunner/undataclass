import decimal

class Item:
    __slots__ = ('name', 'price', 'slug')
    __match_args__ = ('name', 'price')

    def __init__(self, name: str, price: decimal.Decimal) -> None:
        self.name = name
        self.price = price
        self.slug = self.name.lower().replace(' ', '-')

    def __repr__(self):
        cls = type(self).__name__
        return f'{cls}(name={self.name!r}, price={self.price!r})'

    def __eq__(self, other):
        if not isinstance(other, Item):
            return NotImplemented
        return (self.name, self.price) == (other.name, other.price)
