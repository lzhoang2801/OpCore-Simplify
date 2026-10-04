import filecmp
import os
import shutil
import sys
import tempfile
import unittest
import warnings

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Scripts import compat


def make_tree(root):
    os.makedirs(os.path.join(root, "a", "b"))
    os.makedirs(os.path.join(root, "c"))
    with open(os.path.join(root, "top.txt"), "w") as f:
        f.write("top")
    with open(os.path.join(root, "a", "mid.txt"), "w") as f:
        f.write("mid")
    with open(os.path.join(root, "a", "b", "leaf.bin"), "wb") as f:
        f.write(bytes(range(256)))


def same_tree(a, b):
    for root, _dirs, files in os.walk(a):
        rel = os.path.relpath(root, a)
        mirror = b if rel == os.curdir else os.path.join(b, rel)
        for name in files:
            left, right = os.path.join(root, name), os.path.join(mirror, name)
            if not os.path.isfile(right) or not filecmp.cmp(left, right, shallow=False):
                return False
    return True


class CopytreeMergeTest(unittest.TestCase):
    def test_merge_into_existing_destination(self):
        with tempfile.TemporaryDirectory() as tmp:
            src, dst = os.path.join(tmp, "src"), os.path.join(tmp, "dst")
            make_tree(src)
            os.makedirs(dst)
            with open(os.path.join(dst, "prior.txt"), "w") as f:
                f.write("prior")
            compat._copytree_legacy(src, dst)
            self.assertTrue(same_tree(src, dst))
            with open(os.path.join(dst, "prior.txt")) as f:
                self.assertEqual(f.read(), "prior")

    def test_merge_into_new_destination(self):
        with tempfile.TemporaryDirectory() as tmp:
            src, dst = os.path.join(tmp, "src"), os.path.join(tmp, "dst")
            make_tree(src)
            compat._copytree_legacy(src, dst)
            self.assertTrue(same_tree(src, dst))

    def test_nested_byte_fidelity(self):
        with tempfile.TemporaryDirectory() as tmp:
            src, dst = os.path.join(tmp, "src"), os.path.join(tmp, "dst")
            make_tree(src)
            compat._copytree_legacy(src, dst)
            with open(os.path.join(dst, "a", "b", "leaf.bin"), "rb") as f:
                self.assertEqual(f.read(), bytes(range(256)))

    def test_fallback_emits_upgrade_warning(self):
        with tempfile.TemporaryDirectory() as tmp:
            src, dst = os.path.join(tmp, "src"), os.path.join(tmp, "dst")
            make_tree(src)
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                compat._copytree_legacy(src, dst)
            dep = [w for w in caught if issubclass(w.category, DeprecationWarning)]
            self.assertTrue(dep, "expected a DeprecationWarning")
            self.assertIn("upgrade", str(dep[0].message).lower())

    def test_native_delegation_on_modern_python(self):
        with tempfile.TemporaryDirectory() as tmp:
            src, dst = os.path.join(tmp, "src"), os.path.join(tmp, "dst")
            make_tree(src)
            os.makedirs(dst)
            if sys.version_info < (3, 8):
                self.skipTest("native path needs 3.8+")
            compat.copytree_merge(src, dst)
            expected = os.path.join(tmp, "expected")
            shutil.copytree(src, expected, dirs_exist_ok=True)
            self.assertTrue(same_tree(expected, dst))


if __name__ == "__main__":
    unittest.main()
