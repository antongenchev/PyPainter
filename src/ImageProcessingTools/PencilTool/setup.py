from setuptools import setup
from Cython.Build import cythonize

setup(
    name="PencilTool",
    ext_modules=cythonize("PencilTool.py")
)
