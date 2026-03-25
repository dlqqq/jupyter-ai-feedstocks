#!/usr/bin/env python3
"""Update a feedstock recipe's version and sha256 from PyPI."""

import json
import re
import sys
import urllib.request
from pathlib import Path


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <recipe_path> <version>")
        sys.exit(1)

    recipe_path = Path(sys.argv[1])
    version = sys.argv[2]
    text = recipe_path.read_text()

    # Get PyPI package name
    m = re.search(r'pypi\.org/packages/source/./([^/${}]+)/', text)
    if not m:
        m = re.search(r'context:\s*\n(?:.*\n)*?\s+name:\s*(\S+)', text)
    if not m:
        print("Could not determine PyPI package name", file=sys.stderr)
        sys.exit(1)
    pypi_name = m.group(1)

    # Fetch sha256
    with urllib.request.urlopen(f"https://pypi.org/pypi/{pypi_name}/{version}/json", timeout=10) as r:
        data = json.loads(r.read())
    sha256 = next(u["digests"]["sha256"] for u in data["urls"] if u["url"].endswith(".tar.gz"))

    # Update version
    text = re.sub(
        r'(context:\s*\n(?:.*\n)*?\s+version:\s*)["\'][^"\']+["\']',
        f'\\g<1>"{version}"',
        text,
    )

    # Update sha256
    text = re.sub(r'(sha256:\s*)[0-9a-f]{64}', f'\\g<1>{sha256}', text)

    # Reset build number to 0
    text = re.sub(r'(  number:\s*)\d+', r'\g<1>0', text)

    recipe_path.write_text(text)
    print(f"Updated {pypi_name} to {version} (sha256: {sha256[:12]}...)")


if __name__ == "__main__":
    main()
