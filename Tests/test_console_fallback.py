import codecs
import io
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Scripts import utils


class EncodingStdout(io.StringIO):
    """StringIO that encodes writes with the given codec, like a real console."""

    def __init__(self, encoding):
        super().__init__()
        self._codec = encoding

    def write(self, s):
        s.encode(self._codec)
        return super().write(s)


def render_head(stdout_encoding):
    u = utils.Utils.__new__(utils.Utils)
    u.script_name = "OpCore Simplify"
    buf = EncodingStdout(stdout_encoding)
    old_stdout, old_system = sys.stdout, os.system
    sys.stdout, os.system = buf, lambda *a, **k: 0
    try:
        u.head("Check for Updates", resize=False)
    finally:
        sys.stdout, os.system = old_stdout, old_system
    return buf.getvalue()


class ConsoleFallbackTest(unittest.TestCase):
    def test_cp1252_falls_back_to_ascii_without_error(self):
        out = render_head("cp1252")
        lines = out.splitlines()
        self.assertEqual(len(lines), 3)
        self.assertTrue(all(len(line) == 68 for line in lines))
        self.assertTrue(lines[0].startswith("+") and lines[0].endswith("+"))
        self.assertIn("Check for Updates", lines[1])
        out.encode("cp1252")

    def test_utf8_keeps_box_drawing(self):
        out = render_head("utf-8")
        self.assertIn("╔", out)
        self.assertIn("Check for Updates", out)


if __name__ == "__main__":
    unittest.main()
