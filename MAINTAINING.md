# Maintaining pyfastnoiselite-ledfx

This is a fork of [tizilogic/PyFastNoiseLite](https://github.com/tizilogic/PyFastNoiseLite)
with a stable-ABI build, armv7l wheels and CI on top. It wraps
[FastNoise Lite](https://github.com/Auburn/FastNoiseLite), vendored as the git
submodule `ext/FastNoise`.

## What keeps it current

| What | How | Who acts |
| --- | --- | --- |
| GitHub Actions, uv.lock, Python deps | Renovate, from the org preset `github>LedFx/renovate-config`. Non-majors automerge on green CI after 14 days; majors wait 30 days and need a person. | Renovate; majors reviewed by a maintainer |
| FastNoise Lite | Renovate's git-submodules manager on `ext/FastNoise`. Never automerged: it changes the compiled wheel, and possibly the noise LedFx renders. | Maintainer reviews |
| Upstream fork | Renovate bumps the marker below when `tizilogic/PyFastNoiseLite` moves. The PR is the prompt to review upstream. | Maintainer reviews |
| New Python releases | Nothing to rebuild: the `cp311-abi3` wheels already install on new CPython versions. Add the version to `[tool.cibuildwheel] build` so CI tests it. | Maintainer |
| New NumPy releases | Weekly scheduled CI builds and tests every wheel against the newest NumPy. | Whoever sees the red run |
| Workflow security | zizmor on every change to `.github/` and weekly. | CI |

## Output must not drift

`tests/test_noise.py` checks the output against values taken from upstream's
0.0.7 wheel, using the settings LedFx's noise effects use. If a FastNoise Lite
bump or a build change moves those values, the LedFx effects change how they
look. Decide that on purpose. Don't just regenerate the numbers.

## Syncing upstream

Last reviewed upstream commit (Renovate updates this line):

upstream: https://github.com/tizilogic/PyFastNoiseLite main@3b6390f486dd837d6f80fe1cd5bc097c752eb6aa

When Renovate opens a PR bumping it:

```sh
git remote add upstream https://github.com/tizilogic/PyFastNoiseLite  # once
git fetch upstream
git log --oneline <old-sha>..upstream/main
```

The packaging here differs from upstream (pyproject metadata, setuptools-scm,
abi3, tests), so port changes to `src/` by hand or `git cherry-pick -x` and
resolve. Skip upstream CI/release changes; ours is different. Merge the marker
bump in the same PR as the ports, or on its own if nothing applies.

If upstream merges and releases
[tizilogic/PyFastNoiseLite#3](https://github.com/tizilogic/PyFastNoiseLite/pull/3),
LedFx can go back to depending on `pyfastnoiselite`, and this fork can be archived.

## Releasing

Tag `vX.Y.Z` on `main`. setuptools-scm takes the version from the tag. CI
builds the wheels and the sdist, then publishes to PyPI through trusted
publishing from the `pypi` environment, with attestations.

## Repository settings

These live in GitHub, not in this repo. Renovate's automerge relies on them:

- Ruleset `main`: changes go through PRs (no approval needed), no force pushes
  or deletion, and these checks must pass (from GitHub Actions only): the six
  wheel builds, the sdist build, the oldest-NumPy test and zizmor. Repo admins
  can bypass it on a PR. Rename a job and you must update the ruleset too.
- `pypi` environment: deploys from `v*` tags only.
- Actions: workflow token is read-only by default and can't approve PRs.
- Security: Dependabot alerts are on, so Renovate can read them and raise
  `[SECURITY]` PRs straight away. Dependabot security updates are off, so each
  advisory gets only one PR. Secret scanning, push protection and private
  vulnerability reporting are on.
- Renovate skips forks that have no config, so `renovate.json` must stay on
  `main`. Its runs are on the Mend dashboard (developer.mend.io).
- Issues are enabled, for Renovate's Dependency Dashboard and for bug reports.

## Supported versions

CPython 3.11+ and NumPy >= 1.23.2. When a CPython version reaches end of life,
drop it from `[tool.cibuildwheel] build`. When 3.11 goes, raise
`requires-python`, `Py_LIMITED_API` in `setup.py` and the `py_limited_api` tag
together. Also raise the NumPy floor to the first release with wheels for the
new oldest Python. The `numpy_oldest` CI job reads that floor from
pyproject.toml.
