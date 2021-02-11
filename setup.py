import pathlib
import setuptools


setuptools.setup(
    long_description=pathlib.Path("README.rst").read_text(encoding="utf8"),
)
