from setuptools import setup
from Cython.Build import cythonize

setup(
    name="SelectTool",
    ext_modules=cythonize("SelectTool.py")
)
