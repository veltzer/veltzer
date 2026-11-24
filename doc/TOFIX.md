# TOFIX

Findings from a code scan on 2026-10-04.

## Medium

- `pyproject.toml:9` - `ruff` and `mypy` (line 10) are listed in `[project].dependencies` as well as in the `dev` dependency group; they are lint tools, not runtime dependencies of the scripts. Remove them from `[project].dependencies`, leaving only `PyYAML` there.
- `pyproject.toml:16` - `pytest` is a declared dev dependency but there are no tests and no `[processor.pytest]`. `scripts/gen_readme.py:65` (`render`/`render_extra`) is pure and easy to test with a small inline profiles dict (children indentation, badge with/without url, heading extras); add such a test plus a pytest processor, or drop `pytest`.

## Low

- `rsconstruct.toml:20` - several committed files are checked by no processor: `pyproject.toml` and `rsconstruct.toml` (no `[processor.taplo]`), `.github/dependabot.yml` despite a committed `.yamllint.yaml` (no yaml processor), and `config/project.lua` (no `[processor.luacheck]`). Add the matching processors as the other fleet repos do.
- `.rsconstructignore:1` - the file is the unmodified boilerplate (only comments and commented-out examples) and excludes nothing; delete it.
- `links.txt:1` - an unreferenced scratch list of other people's profile READMEs and badge services; nothing in the repo uses it. Delete it, or fold the still-wanted ideas into `README.md.in` / `profiles.yaml`.
- `scripts/gen_readme.py:60` - `data.get("groups")` raises `AttributeError` instead of a clean `die()` when `profiles.yaml` is empty or not a mapping; check `isinstance(data, dict)` first.
