#!/usr/bin/env python

"""
Refresh the sibling ../data checkout and regenerate README.md from it.

README.md is generated from README.md.in plus ../data/yaml/profiles.yaml, but
that generation is deliberately not part of the build: the sibling data repo is
private and is not checked out in CI, and README.md is committed. GitHub serves
it straight from the default branch, so a push is the publish -- there is no
deploy step a build could feed.

Run this by hand after editing profiles.yaml in the data repo, then commit the
resulting README.md. The same profiles.yaml also drives the About page of
../veltzer.github.io via that repo's own scripts/gen_profiles.py, which is
manual for the same reason.

Pulls the data repo (unless --no-pull) and then runs gen_readme.py. Exits
non-zero if the data repo is missing, if the pull fails, or if the generation
fails, so a stale README is never mistaken for an up-to-date one.
"""

import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_REPO = REPO_ROOT.parent / "data"
SOURCE = DATA_REPO / "yaml" / "profiles.yaml"
GEN_README = REPO_ROOT / "scripts" / "gen_readme.py"


def die(message):
    """Print an error to stderr and exit non-zero."""
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(1)


def run(args, cwd=None):
    """Run a command, returning its CompletedProcess; die on failure."""
    result = subprocess.run(args, cwd=cwd, check=False)
    if result.returncode != 0:
        die(f"command failed ({result.returncode}): {' '.join(str(a) for a in args)}")
    return result


def pull_data():
    """Fast-forward the sibling data checkout.

    Refuses to pull over local modifications: `git pull` would either fail
    halfway or silently merge, and neither is something a helper script should
    decide on the user's behalf.
    """
    if not (DATA_REPO / ".git").is_dir():
        die(
            f"No git checkout at {DATA_REPO}. Clone it alongside this repo:\n"
            f"  git clone git@github.com:veltzer/data.git {DATA_REPO}"
        )
    dirty = subprocess.run(
        ["git", "-C", str(DATA_REPO), "status", "--porcelain"],
        capture_output=True,
        text=True,
        check=False,
    )
    if dirty.stdout.strip():
        die(
            f"{DATA_REPO} has uncommitted changes; commit or stash them first, "
            "or re-run with --no-pull to use the working tree as it stands."
        )
    print(f"pulling {DATA_REPO} ...")
    run(["git", "-C", str(DATA_REPO), "pull", "--ff-only"])


def main():
    """Refresh the data checkout and regenerate README.md."""
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument(
        "--no-pull",
        action="store_true",
        help="skip the git pull and generate from the current ../data checkout",
    )
    args = parser.parse_args()

    if args.no_pull:
        print(f"skipping pull; using {DATA_REPO} as it stands")
    else:
        pull_data()

    if not SOURCE.is_file():
        die(f"Missing source file {SOURCE} even after refreshing {DATA_REPO}.")

    print(f"regenerating README.md from {SOURCE} ...")
    run([sys.executable, str(GEN_README)])
    print("done -- review and commit README.md if it changed")


if __name__ == "__main__":
    main()
