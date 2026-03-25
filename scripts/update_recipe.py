#!/usr/bin/env python3
"""Update a feedstock recipe to a given version using PyPI metadata."""

import json
import re
import sys
import urllib.request
from pathlib import Path


def get_pypi_metadata(name: str, version: str) -> dict:
    with urllib.request.urlopen(
        f"https://pypi.org/pypi/{name}/{version}/json", timeout=10
    ) as r:
        return json.loads(r.read())


def get_sha256(metadata: dict) -> str:
    for url_info in metadata.get("urls", []):
        if url_info["url"].endswith(".tar.gz"):
            return url_info["digests"]["sha256"]
    raise ValueError("No source distribution (.tar.gz) found")


def get_run_deps(metadata: dict) -> list[str]:
    """Extract required (non-optional) dependencies from PyPI metadata."""
    requires = metadata["info"].get("requires_dist") or []
    deps = []
    for req in requires:
        # Skip optional/extra dependencies
        if "extra ==" in req:
            continue
        # Parse package name and version spec
        # e.g. "traitlets (>=5.6,<6)" or "pydantic>=2.10.0,<3"
        m = re.match(r"([A-Za-z0-9_.-]+)\s*(?:\(([^)]+)\)|(.*))?", req)
        if not m:
            continue
        name = m.group(1).lower().replace("_", "-")
        version_spec = (m.group(2) or m.group(3) or "").strip()
        # Strip any environment markers after semicolon
        if ";" in version_spec:
            version_spec = version_spec[: version_spec.index(";")].strip()
        if version_spec:
            deps.append(f"{name} {version_spec}")
        else:
            deps.append(name)
    return deps


def format_conda_dep(dep: str) -> str:
    """Convert a PyPI dependency string to conda-forge format."""
    # Already in good shape, just normalize separators
    return dep.replace("(", "").replace(")", "")


def update_recipe(recipe_path: Path, version: str, sha256: str, run_deps: list[str]):
    text = recipe_path.read_text()

    # Update version
    text = re.sub(
        r'(context:\s*\n(?:.*\n)*?\s+version:\s*)["\'][^"\']+["\']',
        f'\\g<1>"{version}"',
        text,
    )

    # Update sha256
    text = re.sub(
        r'(sha256:\s*)[0-9a-f]{64}',
        f"\\g<1>{sha256}",
        text,
    )

    # Update run dependencies
    # Find the run section under requirements
    run_pattern = re.compile(
        r'(  run:\n)((?:    - .+\n)+)',
        re.MULTILINE,
    )
    m = run_pattern.search(text)
    if m and run_deps:
        # Always keep python as first dep
        new_run = "  run:\n    - python >=${{ python_min }}\n"
        for dep in run_deps:
            conda_dep = format_conda_dep(dep)
            # Skip python itself
            if conda_dep.startswith("python ") or conda_dep == "python":
                continue
            new_run += f"    - {conda_dep}\n"
        text = text[: m.start()] + new_run + text[m.end() :]

    # Reset build number to 0
    text = re.sub(r'(  number:\s*)\d+', r'\g<1>0', text)

    recipe_path.write_text(text)


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <recipe_path> <version>")
        sys.exit(1)

    recipe_path = Path(sys.argv[1])
    version = sys.argv[2]

    # Get PyPI package name from recipe
    text = recipe_path.read_text()
    m = re.search(r'pypi\.org/packages/source/./([^/${}]+)/', text)
    if m:
        pypi_name = m.group(1)
    else:
        # Fall back to context name
        m = re.search(r'context:\s*\n(?:.*\n)*?\s+name:\s*(\S+)', text)
        if not m:
            print("Could not determine PyPI package name", file=sys.stderr)
            sys.exit(1)
        pypi_name = m.group(1)

    print(f"Updating {pypi_name} to {version}...")
    metadata = get_pypi_metadata(pypi_name, version)
    sha256 = get_sha256(metadata)
    run_deps = get_run_deps(metadata)

    print(f"  sha256: {sha256}")
    print(f"  deps: {run_deps}")

    update_recipe(recipe_path, version, sha256, run_deps)
    print("  ✅ recipe updated")


if __name__ == "__main__":
    main()
