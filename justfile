# Pull latest main for all feedstock submodules
pull-all:
    git submodule foreach 'git checkout main && git pull'

# List PyPI versions newer than each feedstock's current version
list-missing-versions: pull-all
    python3 scripts/missing_versions.py
