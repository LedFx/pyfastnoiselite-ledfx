"""Output must match upstream pyfastnoiselite 0.0.7 (the cp313 wheel on PyPI).

LedFx effects depend on the exact noise field, so a build or FastNoiseLite
change that shifts these values is a visible change, not a refactor. The
tolerance only absorbs compiler differences such as FMA contraction.
"""

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
    np.testing.assert_allclose(result, expected, rtol=0, atol=1e-6)


def test_get_noise_matches_upstream():
    noise = FastNoiseLite(seed=1337)
    noise.noise_type = NoiseType.NoiseType_OpenSimplex2S
    assert noise.get_noise(34, 22) == pytest.approx(0.7130074501037598, abs=1e-6)
    assert noise.get_noise(100, 110) == pytest.approx(-0.3495847284793854, abs=1e-6)
    assert noise.get_noise(95, 100, 30) == pytest.approx(-0.4522402286529541, abs=1e-6)

