# pyfastnoiselite-ledfx
> **Note:** This is a fork of the original [PyFastNoiseLite](https://github.com/tizilogic/PyFastNoiseLite) maintained by the [LedFx](https://github.com/LedFx) team.
>
> **Why this fork exists:**
> - The original project is sporadically active, and its 0.0.7 release has no Python 3.14 wheels and no sdist on PyPI
> - We build against the CPython stable ABI, so one wheel per platform covers Python 3.11 and every later release
> - We ship armv7l wheels for 32-bit Raspberry Pi OS
> - LedFx depends on pyfastnoiselite and needs a reliable, up-to-date release
>
> All credit for pyfastnoiselite goes to Tiziano Bettio, and for FastNoise Lite to Jordan Peck (Auburn). This fork exists solely to provide maintained releases for projects that depend on it. The build changes are offered upstream in [tizilogic/PyFastNoiseLite#3](https://github.com/tizilogic/PyFastNoiseLite/pull/3).
>
> **Original project:** https://github.com/tizilogic/PyFastNoiseLite\
> **This fork:** https://github.com/LedFx/pyfastnoiselite-ledfx

[![image](https://img.shields.io/pypi/v/pyfastnoiselite-ledfx.svg)](https://pypi.org/p/pyfastnoiselite-ledfx)[![image](https://img.shields.io/pypi/l/pyfastnoiselite-ledfx.svg)](https://pypi.org/p/pyfastnoiselite-ledfx)[![image](https://img.shields.io/pypi/wheel/pyfastnoiselite-ledfx.svg)](https://pypi.org/p/pyfastnoiselite-ledfx)[![image](https://img.shields.io/pypi/pyversions/pyfastnoiselite-ledfx.svg)](https://pypi.org/p/pyfastnoiselite-ledfx)

A Cython wrapper for Auburn's [FastNoise Lite](https://github.com/Auburn/FastNoiseLite) noise generation library.

## Installation

```bash
pip install pyfastnoiselite-ledfx
```

Binary wheels are published for CPython 3.11+ on Windows (x86_64), macOS (x86_64, arm64) and Linux glibc/musl (x86_64, aarch64, armv7l). Building from the sdist needs a C++11 compiler.

The distribution is renamed but the import name is unchanged, so it is a drop-in replacement for `pyfastnoiselite`. Don't install both: they provide the same module.

> **Note:** This wrapper lacks the domain warping functionality.

## Usage

```py
from pyfastnoiselite.pyfastnoiselite import FastNoiseLite, NoiseType

# Initializing with seed
noise = FastNoiseLite(seed=1337)
# Set noise type (optional, defaults to OpenSimplex2)
noise.noise_type = NoiseType.NoiseType_OpenSimplex2S

# Get 2D noise
print(noise.get_noise(34, 22))  # 0.7130074501037598
print(noise.get_noise(100, 110))  # -0.3495847284793854

# Get 3D noise
print(noise.get_noise(95, 100, 30))  # -0.4522402286529541


import numpy as np

Xs = [3, 57, 95]
Ys = [4, 13, 100]
Zs = [0, -4, 30]
coords = np.array([Xs, Ys, Zs], dtype=np.float32)
# Generate noise for each coordinate
print(noise.gen_from_coords(coords))
```

For many points, `gen_from_coords` is much faster than calling `get_noise` in a Python loop. It takes a `float32` array of shape `(2, N)` or `(3, N)` (read-only arrays and views are fine) and returns a `float32` array of shape `(N,)`.

For batches of 1024 points or more, `gen_from_coords` releases the GIL, so separate `FastNoiseLite` instances can generate in parallel threads. Don't change an instance's settings from another thread while it is generating.

## License

This project is licensed under the [MIT license](LICENSE). FastNoise Lite is also MIT licensed.
