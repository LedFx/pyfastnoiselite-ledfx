import platform
import sysconfig

from Cython.Build import cythonize
from setuptools import Extension, setup

# Build against the stable ABI so one wheel per platform covers CPython 3.11+.
# 3.11 is the first version whose limited API has the buffer protocol that
# typed memoryviews need. Free-threaded builds have no stable ABI.
LIMITED_API = not sysconfig.get_config_var("Py_GIL_DISABLED")

if platform.system() == "Windows":
    CXX_ARGS = []
elif platform.system() == "Darwin":
    CXX_ARGS = ["-std=c++11", "-stdlib=libc++"]
else:
    CXX_ARGS = ["-std=c++11"]

extension = Extension(
    "pyfastnoiselite.pyfastnoiselite",
    ["src/pyfastnoiselite/pyfastnoiselite.pyx"],
    include_dirs=["ext/FastNoise", "ext/CPPWrapper"],
    extra_compile_args=CXX_ARGS,
    extra_link_args=CXX_ARGS,
    language="c++",
    define_macros=[("Py_LIMITED_API", "0x030B0000")] if LIMITED_API else [],
    py_limited_api=LIMITED_API,
)

setup(
    ext_modules=cythonize(
        [extension],
        compiler_directives={"language_level": 3, "embedsignature": True},
    ),
    options={"bdist_wheel": {"py_limited_api": "cp311"}} if LIMITED_API else {},
)
