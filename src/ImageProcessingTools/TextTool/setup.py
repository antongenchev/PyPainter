from setuptools import setup
from Cython.Build import cythonize

setup(
    name="TextTool",
    ext_modules=cythonize("TextTool.py")
)
