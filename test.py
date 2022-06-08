from pathlib import Path
import unittest

from undataclass import undataclass


class TestUndataclass(unittest.TestCase):

    maxDiff = 10_000

    def validate(self, module_name):
        tests = Path(__file__).parent / "test_files"
        filename = f"{module_name}.py"
        before = Path(tests / "before" / filename).read_text()
        after = Path(tests / "after" / filename).read_text()
        self.assertEqual(undataclass(before) + "\n", after)

    def test_from_import_no_args_no_fields_or_defaults(self):
        self.validate("simple")

    def test_slots_and_frozen_args_with_default_and_factory(self):
        self.validate("frozen_and_slots")


if __name__ == "__main__":
    unittest.main(verbosity=2)
