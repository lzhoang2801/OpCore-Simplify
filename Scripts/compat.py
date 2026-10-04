import os
import shutil
import sys
import warnings


def _copytree_legacy(src, dst):
    warnings.warn(
        "Merging directory trees on Python {}.{}; "
        "please upgrade to Python 3.8 or newer for "
        "long-term support.".format(*sys.version_info[:2]),
        DeprecationWarning,
    )
    for root, _dirs, files in os.walk(src):
        rel = os.path.relpath(root, src)
        target_root = dst if rel == os.curdir else os.path.join(dst, rel)
        if not os.path.isdir(target_root):
            os.makedirs(target_root)
        for name in files:
            shutil.copy2(os.path.join(root, name), os.path.join(target_root, name))
    return dst


def copytree_merge(src, dst):
    if sys.version_info >= (3, 8):
        return shutil.copytree(src, dst, dirs_exist_ok=True)
    return _copytree_legacy(src, dst)
