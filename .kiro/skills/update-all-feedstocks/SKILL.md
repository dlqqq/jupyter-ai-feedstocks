# Update All Feedstocks

Update all conda-forge feedstocks in this repo to their latest PyPI versions.

## Steps

### Step 1: Prerequisites

Verify that `just` and `python3` are available in the current environment by running:

```bash
just --version && python3 --version
```

If either is missing, inform the user and stop.

### Step 2: List Missing Versions

Run the following to pull latest changes and list feedstocks that are behind PyPI:

```bash
just list-missing-versions
```

This will:

1. Pull the latest `main` branch for all feedstock submodules (in parallel)
2. Compare each feedstock's `recipe/recipe.yaml` version against PyPI
3. Print any packages with newer versions available

If all feedstocks are up to date, report that to the user and stop.

After listing missing versions, write a `TODO.md` file in the repo root with a checklist of packages to update. Only include the **earliest** missing version per package. Example:

```markdown
# Pending Updates

- [ ] jupyter-ai-acp-client → 0.0.8
  - [ ] Opened PR (link: TODO)
  - [ ] Re-rendered via '@conda-forge-admin, please rerender'
- [ ] jupyter-ai-litellm → 0.0.2
  - [ ] Opened PR (link: TODO)
  - [ ] Re-rendered via '@conda-forge-admin, please rerender'
```

If any packages have additional versions beyond the earliest, list them in a separate section:

```markdown
# Remaining Versions (DO NOT UPDATE)

- jupyter-ai-acp-client: 0.0.9, 0.1.0
```

If there are no remaining versions, omit this section.

If `TODO.md` already exists, overwrite it.

Present the `TODO.md` to the user and ask for confirmation before proceeding.

### Step 3: Ensure Forks

Run the following to ensure a GitHub fork and remote exists for each feedstock:

```bash
just ensure-forks
```

This will, for each feedstock submodule:

1. Check if a git remote named `fork` already exists (skip if so)
2. Create a GitHub fork via `gh repo fork`
3. Add it as a remote named `fork`
4. Set the default repo to the upstream (origin) for `gh` CLI commands

### Step 4: Update Each Feedstock

For each package with missing versions, update to the **earliest** missing version only. For example, if a package is missing 0.1.1 and 0.1.2, only update to 0.1.1.

For each package, do the following:

#### 4a: Update version and hash

Run the update script to set the new version and sha256 in the recipe:

```bash
python3 scripts/update_version_and_hash.py <feedstock>/recipe/recipe.yaml <version>
```

#### 4b: Update run dependencies

Get the current dependencies from PyPI:

```bash
curl -s https://pypi.org/pypi/<pypi_name>/json | jq '.info.requires_dist'
```

Use this to update the `requirements.run` section in `recipe/recipe.yaml`. Follow conda-forge formatting conventions:

- Always keep `python >=${{ python_min }}` as the first run dependency
- Ignore optional/extra dependencies (those with `extra ==` markers)
- Use conda-forge package names (e.g. hyphens not underscores). If a dependency is newly added (not in the previous recipe), verify it exists with `conda search -c conda-forge <package>`. If not found, try swapping hyphens/underscores and search again.
- Format version constraints like: `package >=1.0,<2`

#### 4c: Create branch, commit, push, and open PR

```bash
cd <feedstock>
git switch -c update-to-<version>
git add recipe/recipe.yaml
git commit -m "Update to <version>"
git push fork update-to-<version>
gh pr create --base main --title "Update to <version>" --body "<pr_body>"
```

For the PR body, fill out the conda-forge PR template checklist. Check off items that apply:

```
Checklist
- [x] Used a personal fork of the feedstock to propose changes
- [ ] Bumped the build number (if the version is unchanged)
- [x] Reset the build number to `0` (if the version changed)
- [x] Re-rendered with the latest `conda-smithy`
- [x] Ensured the license file is being packaged.
```

After opening the PR, trigger a re-render by adding a comment:

```bash
gh pr comment --body "@conda-forge-admin, please rerender"
```

After each PR is successfully opened, mark the corresponding item in `TODO.md` as done by changing `- [ ]` to `- [x]`, and add the PR link as a sub-bullet. Example:

```markdown
- [x] jupyter-ai-acp-client → 0.0.8
  - [x] Opened PR (link: https://github.com/conda-forge/jupyter-ai-acp-client-feedstock/pull/3)
  - [ ] Re-rendered via '@conda-forge-admin, please rerender'
```

Read `TODO.md` before each package to check what's remaining.

### Step 5: Summary

After all PRs are opened, present a summary to the user:

1. List each PR opened with the version change and link, e.g.:
   ```
   jupyter-ai-acp-client: 0.0.7 → 0.0.8 — https://github.com/conda-forge/jupyter-ai-acp-client-feedstock/pull/3
   ```

2. List any remaining versions that still need updating (i.e. versions beyond the earliest that were skipped), e.g.:
   ```
   Still pending:
   - jupyter-ai-acp-client: 0.0.9, 0.1.0
   ```

   If there are no remaining versions, say so.
