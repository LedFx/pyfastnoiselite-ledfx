"""Output must match upstream pyfastnoiselite 0.0.7 (the cp313 wheel on PyPI).

LedFx effects depend on the exact noise field, so a build or FastNoiseLite
change that shifts these values is a visible change, not a refactor.

The tolerance absorbs compiler differences only: GCC on aarch64 fuses
multiply-adds and lands up to ~5e-6 away from these x86_64 values, as
upstream's own aarch64 wheel does. That is far below one 8-bit LED step
(~4e-3); a real algorithm change moves values by orders of magnitude more.
"""

ATOL = 1e-5

import numpy as np
import pytest

from pyfastnoiselite.pyfastnoiselite import FastNoiseLite, FractalType, NoiseType

XS = [3.0, 57.25, -95.5, 0.125, 1000.0, -0.75]
YS = [4.0, -13.5, 100.0, 7.75, -250.0, 0.5]
ZS = [0.0, -4.0, 30.5, 2.25, 12.0, -8.0]


def opensimplex2(frequency, fbm=False):
    noise = FastNoiseLite()
    noise.noise_type = NoiseType.NoiseType_OpenSimplex2
    noise.frequency = frequency
    if fbm:
        noise.fractal_type = FractalType.FractalType_FBm
        noise.fractal_octaves = 4
        noise.fractal_lacunarity = 2.0
        noise.fractal_gain = 0.5
    return noise


# Settings used by LedFx's soap2d, noise2d and smoke2d effects
@pytest.mark.parametrize(
    ("noise", "coords", "expected"),
    [
        pytest.param(
            opensimplex2(0.3),
            [XS, YS],
            [-0.18366515636444092, -0.5827328562736511, -0.16304421424865723,
             0.19245024025440216, -0.9289402961730957, -0.02339748665690422],
            id="2d",
        ),
        pytest.param(
            opensimplex2(0.6),
            [XS, YS, ZS],
            [-0.4824860990047455, -0.4279617369174957, 0.25307297706604004,
             -0.28847619891166687, 0.3031725287437439, 0.17418509721755981],
            id="3d",
        ),
        pytest.param(
            opensimplex2(0.6, fbm=True),
            [XS, YS, ZS],
            [-0.3643673062324524, -0.15223930776119232, 0.10556774586439133,
             -0.27169501781463623, 0.3763471245765686, -0.03109687566757202],
            id="3d-fbm",
        ),
    ],
)
def test_gen_from_coords_matches_upstream(noise, coords, expected):
    result = noise.gen_from_coords(np.array(coords, dtype=np.float32))
    assert result.dtype == np.float32
    np.testing.assert_allclose(result, expected, rtol=0, atol=ATOL)


def test_get_noise_matches_upstream():
    noise = FastNoiseLite(seed=1337)
    noise.noise_type = NoiseType.NoiseType_OpenSimplex2S
    assert noise.get_noise(34, 22) == pytest.approx(0.7130074501037598, abs=ATOL)
    assert noise.get_noise(100, 110) == pytest.approx(-0.3495847284793854, abs=ATOL)
    assert noise.get_noise(95, 100, 30) == pytest.approx(-0.4522402286529541, abs=ATOL)



def test_accepts_read_only_and_broadcast_arrays():
    coords = np.array([XS, YS, ZS], dtype=np.float32)
    expected = opensimplex2(0.6).gen_from_coords(coords)
    coords.setflags(write=False)
    np.testing.assert_array_equal(opensimplex2(0.6).gen_from_coords(coords), expected)
    column = np.broadcast_to(coords[:, :1], (3, 5))
    np.testing.assert_array_equal(
        opensimplex2(0.6).gen_from_coords(column), np.full(5, expected[0])
    )


@pytest.mark.parametrize("rows", [0, 1, 4])
def test_rejects_wrong_number_of_rows(rows):
    # An explicit check, not an assert: it must hold under python -O too,
    # because the generation loop runs without bounds checks.
    with pytest.raises(ValueError, match=r"shape \(2, N\) or \(3, N\)"):
        FastNoiseLite().gen_from_coords(np.zeros((rows, 4), dtype=np.float32))


def test_rejects_enum_of_the_wrong_type():
    noise = FastNoiseLite()
    with pytest.raises(ValueError):
        noise.noise_type = FractalType.FractalType_FBm
    assert noise.noise_type is NoiseType.NoiseType_OpenSimplex2


@pytest.mark.parametrize("count", [10, 5000], ids=["with-gil", "without-gil"])
def test_batch_matches_single_points(count):
    rng = np.random.default_rng(count)
    coords = (rng.random((3, count)) * 200 - 100).astype(np.float32)
    noise = opensimplex2(0.6, fbm=True)
    single = [noise.get_noise(*map(float, point)) for point in coords.T]
    np.testing.assert_array_equal(noise.gen_from_coords(coords), np.float32(single))


def test_parallel_threads_match_serial():
    from concurrent.futures import ThreadPoolExecutor

    rng = np.random.default_rng(0)
    batches = [(rng.random((3, 20000)) * 200 - 100).astype(np.float32) for _ in range(8)]
    serial = [opensimplex2(0.6, fbm=True).gen_from_coords(b) for b in batches]
    with ThreadPoolExecutor(4) as pool:
        parallel = list(pool.map(lambda b: opensimplex2(0.6, fbm=True).gen_from_coords(b), batches))
    for got, want in zip(parallel, serial):
        np.testing.assert_array_equal(got, want)


def test_version_matches_distribution():
    from importlib.metadata import version

    import pyfastnoiselite.pyfastnoiselite as module

    assert module.__version__ == version("pyfastnoiselite-ledfx")


def test_imports_without_package_metadata():
    # PyInstaller bundles (LedFx's Windows and macOS builds) have no
    # dist-info unless the spec copies it; the import must still work.
    import subprocess
    import sys

    code = (
        "import importlib.metadata as md\n"
        "def missing(name): raise md.PackageNotFoundError(name)\n"
        "md.version = missing\n"
        "import pyfastnoiselite.pyfastnoiselite as m\n"
        "print(m.__version__)\n"
    )
    result = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, check=True
    )
    assert result.stdout.strip() == "unknown"
