import sys

import local_ai_lab


def test_python_version():
    assert sys.version_info[:2] == (3, 12)


def test_package_imports():
    assert local_ai_lab is not None
