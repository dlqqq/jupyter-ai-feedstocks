# Pull latest main for all feedstock submodules
pull-all:
    git submodule foreach -q 'echo $sm_path' | xargs -P 100 -I{} sh -c 'cd {} && git switch main -q && git pull -q'

# Pull latest main (sequential, slow)
pull-all-old:
    git submodule foreach 'git checkout main && git pull'

# List PyPI versions newer than each feedstock's current version
list-missing-versions: pull-all
    python3 scripts/missing_versions.py
