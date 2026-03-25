# jupyter-ai-feedstocks

A repo for managing [conda-forge](https://conda-forge.org/) feedstock updates for Jupyter AI packages. Each feedstock is included as a git submodule, and the repo provides tooling to quickly check for outdated versions and open update PRs.

## Requirements

- [just](https://github.com/casey/just)
- [GitHub CLI](https://cli.github.com/) (`gh`), authenticated
- Python 3
- [Kiro](https://kiro.dev)

## Just Recipes

- `just pull-all` — Pull the latest `main` branch for all feedstock submodules in parallel.
- `just list-missing-versions` — Pull all submodules, then compare each feedstock's `recipe/recipe.yaml` version against PyPI and print any packages with newer versions available.
- `just ensure-forks` — Ensure a GitHub fork exists for each feedstock (via `gh repo fork`) and add it as a remote named `fork`. Sets the default `gh` repo to the upstream origin.

## Updating All Feedstocks

This repo includes a [Kiro skill](https://kiro.dev) that automates the entire update workflow. To bump all feedstocks to their latest PyPI versions:

1. Open Kiro in this repo
2. Ask Kiro to use the `update-all-feedstocks` skill

Kiro will pull the latest submodules, identify outdated packages, update each recipe's version/hash/dependencies, and open PRs on conda-forge with re-render requests.
