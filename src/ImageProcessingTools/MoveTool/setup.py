from setuptools import setup
from Cython.Build import cythonize

setup(
    name="MoveTool",
    ext_modules=cythonize("MoveTool.py")
)
