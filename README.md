# undataclass

Turn dataclasses into not-dataclasses

You can [convert a dataclass to a regular class in Python][app] right from your web browser.


## Usage

Given a `my_module.py` file containing one or more dataclasses:

```python
from dataclasses import dataclass, field
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class Item:
    name: str
    price: Decimal = Decimal(0)
    colors: str = field(default_factory=list)
```

You can run the `undataclass.py` script against your `my_module.py` file to output a new equivalent module with dataclasses replaced by non-dataclasses:

```bash
$ python3 undataclass.py my_module.py
from decimal import Decimal

class Item:
    __slots__ = ('name', 'price', 'colors')
    __match_args__ = ('name', 'price', 'colors')

    def __init__(self, name: str, price: Decimal=Decimal(0), colors: str=None) -> None:
        if colors is None:
            colors = list()
        object.__setattr__(self, 'name', name)
        object.__setattr__(self, 'price', price)
        object.__setattr__(self, 'colors', colors)

    def __repr__(self):
        cls = type(self).__name__
        return f'{cls}(name={self.name!r}, price={self.price!r}, colors={self.colors!r})'

    def __eq__(self, other):
        if not isinstance(other, Item):
            return NotImplemented
        return (self.name, self.price, self.colors) == (other.name, other.price, other.colors)

    def __hash__(self):
        return hash((self.name, self.price, self.colors))

    def __setattr__(self, name, value):
        raise AttributeError(f"Can't set attribute {name!r}")

    def __delattr__(self, name):
        raise AttributeError(f"Can't delete attribute {name!r}")

    def __getstate__(self):
        return (self.name, self.price, self.colors)

    def __setstate__(self, state):
        fields = ('name', 'price', 'colors')
        for (field, value) in zip(fields, state):
            object.__setattr__(self, field, value)
```

Note that the generated code isn't PEP8 compliant, but it is fairly readable.
You can either fix up the formatting yourself or run an auto-formatter (like [Black][]) against your code.


## Features & Known Limitations

What (usually) works:

- Pretty much all the arguments you can pass to the `dataclasses.dataclass` decorator
- Type annotations, default values, `InitVar`, and `ClassVar`
- Pretty much all the arguments you can pass to the `fields` helper

What doesn't work:

- Usages of fancy helpers like `dataclasses.fields`, `dataclasses.astuple`, the field `metadata` argument will result in broken output code that you'll need to fix up yourself
- Using `as` imports (e.g. `import dataclasses as dc` doesn't work)
- Lots of assumptions are made that you're using the `dataclasses` module in a pretty "standard" way


## Testing

You can find examples of "before" and "after" code in the `test_files` directory.

Feel free to run the validate these examples yourself to confirm that the `undataclass` script actually generates the expected results:

```bash
$ python test.py
test_from_import_no_args_no_fields_or_defaults (__main__.TestUndataclass)
Tests no-args dataclass, docstring, and no defaults. ... ok
test_inheritance_and_more_default_factories (__main__.TestUndataclass)
Tests dataclass inheritance and lambda factories. ... ok
test_kw_only_initvar_and_match_args (__main__.TestUndataclass)
Tests KW_ONLY pseudo-field, InitVar, and match_args. ... ok
test_post_init (__main__.TestUndataclass)
Tests dataclasses.dataclass, __post_init__ & manual __slots__. ... ok
test_slots_and_frozen_args_with_default_and_factory (__main__.TestUndataclass)
Tests slots, frozen, order, default value, & default_factory. ... ok
test_with_functions_and_regular_class (__main__.TestUndataclass)
Tests non-dataclass and also regular methods. ... ok

----------------------------------------------------------------------
Ran 6 tests in 0.008s

OK
```


[black]: https://black.readthedocs.io
[app]: https://www.pythonmorsels.com/undataclass/
