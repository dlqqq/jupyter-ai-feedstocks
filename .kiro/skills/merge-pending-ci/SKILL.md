# Merge Pending CI

Merge GitHub PRs once their CI checks pass. ONLY RUN THIS SKILL WHEN EXPLICITLY PROMPTED.

## Steps

### Step 1: Get PR List

Ask the user which PRs to merge. Each PR should be identified by its feedstock
directory and PR number, or by a full GitHub URL.

Also ask the user for a deadline time (e.g. "7pm"). If the deadline passes
before all PRs are merged, stop polling and report the remaining PRs as timed
out.

### Step 2: Prevent Sleep

Compute the number of seconds until the deadline and start `caffeinate` in the
background to prevent the laptop from sleeping:

```bash
deadline=$(date -j -f "%Y-%m-%d %H:%M:%S" "<deadline_date> <deadline_time>" +%s)
now=$(date +%s)
remaining=$((deadline - now))
nohup caffeinate -s -t $remaining > /dev/null 2>&1 & disown
```

### Step 3: Poll and Merge

Loop until all PRs are merged:

1. Sleep 5 minutes
2. For each pending PR, check CI status:
   ```bash
   cd <feedstock> && gh pr checks <number>
   ```
3. If all checks pass, get the PR title and merge the PR:
   ```bash
   title=$(cd <feedstock> && gh pr view <number> --json title -q .title)
   cd <feedstock> && gh pr merge <number> --squash -t "$title"
   ```
   Mark the PR as merged.
4. If any check has failed, kick CI by closing and reopening the PR:
   ```bash
   cd <feedstock> && gh pr close <number> && gh pr reopen <number>
   ```
5. If checks are still pending, do nothing.
6. Check the current time via `date +%H:%M` and compare against the deadline.
   If the current time is past the deadline, stop polling and move to the
   summary.
7. Continue polling if any PRs are still not merged.

### Step 4: Summary

Stop `caffeinate`:

```bash
killall caffeinate
```

Once all PRs are resolved, present a report:

```
## Merge Report

Merged:
- <feedstock> #<number> — <pr_title>

Timed Out:
- <feedstock> #<number> — <pr_title>
```

If all PRs merged successfully, omit the "Timed Out" section and vice versa.
