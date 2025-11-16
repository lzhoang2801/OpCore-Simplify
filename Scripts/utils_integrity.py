import hashlib
from pathlib import Path
class IntegrityError(Exception):
    pass

def verify(path: str | Path, expected: str) -> None:
    """Verify SHA256 of a file against expected hash. Raises IntegrityError if mismatch."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    actual = h.hexdigest()
    if actual.lower() != expected.lower():
        raise IntegrityError(f"Checksum mismatch: expected {expected}, got {actual}")
