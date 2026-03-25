#!/usr/bin/env python3
"""Print PyPI versions newer than the current feedstock version for each package."""

import json
import re
import sys
import urllib.request
from pathlib import Path
from packaging.version import Version, InvalidVersion


def get_feedstock_version(recipe: Path) -> str:
    m = re.search(
        r'context:\s*\n(?:.*\n)*?\s+version:\s*["\']([^"\']+)["\']',
        recipe.read_text(),
    )
    if not m:
        raise ValueError(f"Could not parse version from {recipe}")
    return m.group(1)


def get_pypi_name(recipe: Path) -> str:
    text = recipe.read_text()
    # Try literal package name in URL first
    m = re.search(r'pypi\.org/packages/source/./([^/${}]+)/', text)
    if m:
        return m.group(1)
    # Fall back to context name variable (used when URL is templated)
    m = re.search(r'context:\s*\n(?:.*\n)*?\s+name:\s*(\S+)', text)
    if m:
        return m.group(1)
    raise ValueError(f"Could not parse PyPI name from {recipe}")


def get_pypi_versions(name: str) -> list[str]:
    try:
        with urllib.request.urlopen(
            f"https://pypi.org/pypi/{name}/json", timeout=10
        ) as r:
            return list(json.loads(r.read()).get("releases", {}).keys())
    except Exception as e:
        print(f"  ⚠ Failed to fetch PyPI data for {name}: {e}", file=sys.stderr)
        return []


def newer_versions(all_versions: list[str], baseline: str) -> list[str]:
    try:
        base = Version(baseline)
    except InvalidVersion:
        return []
    result = []
    for v in all_versions:
        try:
            if Version(v) > base:
                result.append((Version(v), v))
        except InvalidVersion:
            continue
    result.sort()
    return [v for _, v in result]


def main():
    root = Path(__file__).resolve().parent.parent
    found_any = False

    for fs in sorted(root.glob("*-feedstock")):
        recipe = fs / "recipe" / "recipe.yaml"
        if not recipe.exists():
            continue
        try:
            current = get_feedstock_version(recipe)
            pypi_name = get_pypi_name(recipe)
        except ValueError as e:
            print(f"⚠ {fs.name}: {e}", file=sys.stderr)
            continue

        missing = newer_versions(get_pypi_versions(pypi_name), current)
        if missing:
            found_any = True
            print(f"📦 {pypi_name} (feedstock: {current})")
            for v in missing:
                print(f"   → {v}")
            print()

    if not found_any:
        print("✅ All feedstocks are up to date!")


if __name__ == "__main__":
    main()
