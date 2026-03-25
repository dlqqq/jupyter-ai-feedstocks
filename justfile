# Pull latest main for all feedstock submodules
pull-all:
    git submodule foreach -q 'echo $sm_path' | xargs -P 100 -I{} sh -c 'cd {} && git switch main -q && git pull -q'

# Pull latest main (sequential, slow)
pull-all-old:
    git submodule foreach 'git checkout main && git pull'

# Ensure a GitHub fork exists for each feedstock and set default repo to origin
ensure-forks:
    #!/usr/bin/env bash
    for dir in *-feedstock; do
        cd "$dir"
        if ! git remote get-url fork &>/dev/null; then
            echo "Forking $dir..."
            gh repo fork --remote --remote-name fork
            gh repo set-default "$(git remote get-url origin | sed 's|.*github.com[:/]||;s|\.git$||')"
        fi
        cd ..
    done

# List PyPI versions newer than each feedstock's current version
list-missing-versions: pull-all
    python3 scripts/missing_versions.py

# Update each feedstock to its earliest missing version and open PRs
update-all: pull-all ensure-forks
    python3 scripts/update_all.py
