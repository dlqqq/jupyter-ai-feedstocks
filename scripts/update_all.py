#!/usr/bin/env python3
"""Update each feedstock to its earliest missing version, commit, push, and open a PR."""

import json
import subprocess
import sys
from pathlib import Path


def run(cmd, **kwargs):
    return subprocess.run(cmd, check=True, **kwargs)


def get_origin_repo(feedstock_dir: Path) -> str:
    result = run(
        ["git", "-C", str(feedstock_dir), "remote", "get-url", "origin"],
        capture_output=True, text=True,
    )
    # Parse "git@github.com:org/repo.git" or "https://github.com/org/repo.git"
    url = result.stdout.strip()
    repo = url.split("github.com")[-1].lstrip(":/").removesuffix(".git")
    return repo


def update_feedstock(root: Path, feedstock: str, version: str):
    fs_dir = root / feedstock
    recipe = fs_dir / "recipe" / "recipe.yaml"
    branch = f"update-to-{version}"

    print(f"\n{'='*60}")
    print(f"📦 {feedstock} → {version}")
    print(f"{'='*60}")

    # Update recipe
    run(["python3", str(root / "scripts" / "update_recipe.py"), str(recipe), version])

    # Create branch, commit, push
    run(["git", "-C", str(fs_dir), "switch", "-c", branch])
    run(["git", "-C", str(fs_dir), "add", "recipe/recipe.yaml"])
    run(["git", "-C", str(fs_dir), "commit", "-m", f"Update to {version}"])
    run(["git", "-C", str(fs_dir), "push", "fork", branch])

    # Open PR
    repo = get_origin_repo(fs_dir)
    run([
        "gh", "pr", "create",
        "--repo", repo,
        "--base", "main",
        "--head", f"dlqqq:{branch}",
        "--title", f"Update to {version}",
        "--body", f"Update to version {version} from PyPI.",
    ], cwd=str(fs_dir))


def main():
    root = Path(__file__).resolve().parent.parent
    missing = json.loads(
        subprocess.run(
            ["python3", str(root / "scripts" / "missing_versions.py"), "--json"],
            capture_output=True, text=True, check=True,
        ).stdout
    )

    if not missing:
        print("✅ All feedstocks are up to date!")
        return

    for pkg in missing:
        version = pkg["missing"][0]
        update_feedstock(root, pkg["feedstock"], version)

    print(f"\n✅ Opened {len(missing)} PRs.")


if __name__ == "__main__":
    main()
