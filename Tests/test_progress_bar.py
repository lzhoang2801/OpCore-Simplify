import io
import os
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Scripts import resource_fetcher


class FakeResponse:
    def __init__(self, payload):
        self._stream = io.BytesIO(payload)

    def getheader(self, name):
        return str(len(self._stream.getvalue())) if name == "Content-Length" else None

    def read(self, size=-1):
        return self._stream.read(size)


class EncodingStdout:
    """Minimal stdout stub enforcing an encoding on every write."""

    def __init__(self, encoding):
        self._encoding = encoding
        self._chunks = []

    @property
    def encoding(self):
        return self._encoding

    def write(self, s):
        s.encode(self._encoding)
        self._chunks.append(s)
        return len(s)

    def flush(self):
        pass

    def getvalue(self):
        return "".join(self._chunks)


def run_download(stdout_encoding):
    fetcher = resource_fetcher.ResourceFetcher()
    response = FakeResponse(b"x" * (64 * 1024))
    buf = EncodingStdout(stdout_encoding)
    with tempfile.TemporaryFile() as local_file:
        with patch.object(resource_fetcher.sys, "stdout", buf):
            fetcher._download_with_progress(response, local_file)
    return buf.getvalue()


class ProgressBarEncodingTest(unittest.TestCase):
    def test_cp1252_degrades_to_ascii_without_error(self):
        out = run_download("cp1252")
        out.encode("cp1252")
        self.assertIn("#", out)
        self.assertNotIn("█", out)

    def test_utf8_keeps_block_characters(self):
        out = run_download("utf-8")
        self.assertIn("█", out)


if __name__ == "__main__":
    unittest.main()
