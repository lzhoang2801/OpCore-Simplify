import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Scripts import report_validator

ACCEPT = [
    "\\_TZ_.TZS0",
    "\\_TZ_.FAN0",
    "\\AOD_",
    "\\_SB.PCI0.GPP2",
    "_SB.PCI0",
]

REJECT = [
    "not-a-path!!!",
    "_SB..PCI0",
]


def verdict(value):
    """Run the value through the real wired schema rule and return errors."""
    v = report_validator.ReportValidator()
    rule = v.SCHEMA["schema"]["Network"]["values_rule"]["schema"]["ACPI Path"]
    v._validate_node(value, rule, "Root.Network.DEV0.ACPI Path")
    return v.errors


class AcpiPathValidationTest(unittest.TestCase):
    def test_valid_paths_pass(self):
        for value in ACCEPT:
            with self.subTest(value=value):
                self.assertEqual(verdict(value), [], value)

    def test_malformed_paths_fail(self):
        for value in REJECT:
            with self.subTest(value=value):
                errors = verdict(value)
                self.assertTrue(
                    any("ACPI Path" in e for e in errors),
                    "expected an ACPI Path error for %r, got %r" % (value, errors),
                )


if __name__ == "__main__":
    unittest.main()
