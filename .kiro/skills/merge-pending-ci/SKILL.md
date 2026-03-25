# Merge Pending CI

Merge GitHub PRs once their CI checks pass. ONLY RUN THIS SKILL WHEN EXPLICITLY PROMPTED.

## Steps

### Step 1: Get PR List

Ask the user which PRs to merge. Each PR should be identified by its feedstock
directory and PR number, or by a full GitHub URL.

### Step 2: Poll and Merge

Loop until all PRs are either merged or have failing CI:

1. Sleep 30 seconds
2. For each pending PR, check CI status:
   ```bash
   cd <feedstock> && gh pr checks <number>
   ```
3. If all checks pass, merge the PR:
   ```bash
   cd <feedstock> && gh pr merge <number> --merge
   ```
   Mark the PR as merged.
4. If any check has failed, mark the PR as failed and stop polling it.
5. If checks are still pending, continue polling on the next iteration.

### Step 3: Summary

Once all PRs are resolved, present a report:

```
## Merge Report

Merged:
- <feedstock> #<number> — <pr_title>

Failed CI:
- <feedstock> #<number> — <pr_title> (failed check: <check_name>)
```

If all PRs merged successfully, omit the "Failed CI" section and vice versa.
