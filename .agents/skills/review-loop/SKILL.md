---
name: review-loop
description: "Drive a branch to review-clean. If a GitHub PR exists, watch its CI and auto-address unresolved review comments (replying on each thread), then loop: spawn a reviewer subagent, auto-fix its findings, repeat until clean or 3 rounds. Push once at the end. Use when the user wants to clean up a PR/branch before merge."
---

# Review Loop

Drive the current branch to a review-clean state. Two parts run in order:

1. **PR triage** (only if a GitHub PR exists for this branch): watch CI and resolve unresolved review comments.
2. **Review loop**: repeatedly review the branch and auto-fix findings, up to 3 rounds.

**Usage:** `/review-loop`

Commits are made locally each round. **Push only once, at the very end** (see Step 4). CI is not re-triggered between rounds by design.

---

## Step 0: Establish context

1. Current branch: `git rev-parse --abbrev-ref HEAD`. If it's `main`/`master`, stop and tell the user there's nothing to review against.
2. Base branch: if an open PR exists for this branch, use its base. Stacked PRs target a prior branch rather than `main`, and using the wrong base makes the reviewer (Step 2a) diff against `main...HEAD`, pulling in changes that belong to the parent branch. Prefer the PR's `baseRefName`:
   ```bash
   gh pr view --json baseRefName --jq .baseRefName 2>/dev/null
   ```
   If that returns nothing (no PR), fall back to `main` (or `master` if `main` doesn't exist).
3. Confirm the working tree state with `git status --short`. If there are uncommitted changes, note them; the loop will keep its own commits separate but should not clobber in-progress work. If the tree is dirty in a way that would make committing fixes ambiguous, ask the user before proceeding.

## Step 1: PR triage (skip entirely if no PR)

Check for an open PR on this branch:

```bash
gh pr view --json number,url,headRefName,state 2>/dev/null
```

If this fails or there is no open PR, skip to Step 2.

### 1a: Watch CI (non-blocking, in a subagent)

Spawn a **background** `general-purpose` subagent so CI-watching does not block the review loop. Brief it to:

- Run `gh pr checks <number> --watch` (or poll `gh pr checks <number>`) until all checks conclude.
- Report back, per check: name, conclusion (pass/fail), and for failures the relevant log excerpt via `gh run view <run-id> --log-failed`.
- Return a structured summary of failing checks and their likely causes. Do not fix anything and do not modify the repository (read/query only).

Continue with Step 1b while this runs. When the subagent reports back, fold any CI failures into the review-loop fixes (treat a failing check as a review finding).

### 1b: Resolve unresolved review comments

Fetch review threads (comments from humans and bots like CodeRabbit/Copilot). Use the GraphQL API to get resolution state, since `gh pr view` does not expose it:

```bash
gh api graphql -f query='
query($owner:String!,$repo:String!,$pr:Int!,$cursor:String){
  repository(owner:$owner,name:$repo){
    pullRequest(number:$pr){
      reviewThreads(first:100,after:$cursor){
        pageInfo{ hasNextPage endCursor }
        nodes{
          id isResolved isOutdated
          comments(first:50){ nodes{ id databaseId path line body author{login} } }
        }
      }
    }
  }
}' -f owner=<owner> -f repo=<repo> -F pr=<number> -F cursor=<endCursor>
```

Derive `<owner>`/`<repo>` from `gh repo view --json owner,name`. Page through **all** threads: on the first call pass `-F cursor=null` (use `-F`, not `-f`, so `gh` sends a JSON `null`; `-f cursor=null` would send the string `"null"`, an invalid cursor), then re-run with `-F cursor=<endCursor>` while `pageInfo.hasNextPage` is true. A PR with more than 100 threads would otherwise leave unresolved comments after the first page unaddressed.

For **each thread where `isResolved` is false**, decide one of:

- **Fix**: the comment is valid. Make the code change.
- **Ignore/disagree**: irrelevant, out of scope, or you disagree. Do not change code.

Then **reply on the thread** via `gh` explaining the action, and resolve threads you fixed:

- Reply: `gh api repos/<owner>/<repo>/pulls/<number>/comments/<comment-databaseId>/replies -f body='<reply>'`
  - `<comment-databaseId>` **must be the thread's top-level comment**, i.e. the first entry in the thread's `comments.nodes` (the query returns them in order). GitHub's reply endpoint requires the top-level review comment id and rejects replying to a reply, so on threads that already have replies, using the latest comment's id fails.
  - For fixes: briefly state what you changed.
  - For disagree/ignore: briefly state why (be respectful; this is a public reply).
- Resolve a thread you fixed:
  ```bash
  gh api graphql -f query='mutation($id:ID!){ resolveReviewThread(input:{threadId:$id}){ thread{ isResolved } } }' -f id=<threadId>
  ```
  Do **not** resolve threads you disagreed with; leave them open for the human reviewer.

Commit the comment-driven fixes with a clear message (see Commit conventions below). One commit for this batch is fine.

## Step 2: Review loop (always runs)

Loop up to **3 times**. Track a round counter.

### 2a: Spawn a reviewer subagent

Spawn a fresh **`Explore`** (read-only) subagent each round to review the branch. Use `Explore`, not `general-purpose`: the reviewer must not be able to mutate the branch, and `Explore` has no `Edit`/`Write` tools while still having `Bash` to run checks. (A writable reviewer will sometimes "helpfully" refactor files even when told only to report, which silently pollutes the working tree.) Brief it to:

- Review the branch diff against the base: `git diff <base>...HEAD` and read the changed files in full for context.
- Look for: correctness bugs, logic errors, missing error handling, security issues, broken tests, violations of the project's coding standards (`devdocs/coding-standards.md`) and `CLAUDE.md` conventions (e.g. no emdashes, module organization).
- Run available checks it can (typecheck/lint/tests for the affected package per that package's `AGENTS.md`) and report failures.
- Return a **structured list of findings**, each with: file:line, severity (blocker/should-fix/nit), a concrete description, and a suggested fix. If nothing is wrong, return an empty list explicitly.
- The subagent only reports; it does not change code.

**Guard:** before applying fixes in 2b, capture `git status --short`. After the reviewer returns, confirm it did not modify the working tree (it can't via `Explore`, but this also catches stray edits from checks like formatters). To revert stray edits **without clobbering the user's pre-existing uncommitted work**, do not blanket `git checkout -- <file>`: a file may hold both the user's in-progress changes and a check's edits. Instead:

- If the tree was **clean** at Step 0 for that file, `git checkout -- <file>` is safe.
- If the file had **pre-existing uncommitted changes**, do not check it out. Snapshot the intended state first (e.g. `git stash push -- <files>` before running checks, or save `git diff <file>` to a patch), then restore only the check-induced delta rather than the whole file. When in doubt, leave the file alone and surface the stray edit to the user instead of discarding their work.

**Convention-vs-reality findings:** if a finding is a style rule the surrounding codebase pervasively violates (e.g. emdashes when the whole repo uses them), do not silently rewrite files wholesale. Fix only what this branch added, and surface the broader conflict to the user rather than auto-migrating unrelated code. Never touch user-facing UI strings for a style nit unless asked.

Include any unresolved CI failures from Step 1a as additional findings once known.

### 2b: Auto-fix findings

In the main agent, triage each finding:

- Fix blockers and should-fixes. Apply nits when cheap and clearly correct.
- Skip findings you judge incorrect or out of scope; note briefly why in your response to the user.

After applying fixes, commit them locally (one commit per round is fine; see Commit conventions). Re-run the relevant package checks to confirm the fixes are sound.

### 2c: Decide whether to continue

- If the reviewer returned **no actionable findings** (or only findings you deliberately skipped), the loop is done. Stop.
- Otherwise increment the round counter. If it's **less than 3**, go back to 2a.
- After **3 rounds** with findings still remaining, stop and **report the unresolved findings** to the user in a summary. Do not keep looping.

## Step 3: Verify

Run the affected package's test/lint/typecheck commands once more (per its `AGENTS.md`) to confirm the branch is green locally. Report results honestly, including any still-failing checks.

## Step 4: Push (once, at the end)

Push all the commits made during this run:

```bash
git push
```

(Use `git push -u origin <branch>` if the branch has no upstream.) This updates the PR and re-triggers CI. If there is no PR, pushing still updates the remote branch.

Report a final summary:
- CI status found in Step 1 and whether failures were addressed.
- Review comments: how many fixed vs. left open (with reasons).
- Review-loop rounds run and what was fixed each round.
- Any findings intentionally left unresolved.

## Commit conventions

Follow the repo conventions from `CLAUDE.md`:
- Imperative subject, capitalized, no trailing period, ~50 chars.
- Body wrapped at 72 chars explaining what and why.
- **No AI attribution** (a pre-commit hook blocks `Co-Authored-By: Claude` and similar).
- No emdashes (and no fake `--` emdashes) anywhere.
- Stage only the files you changed; never `git add -A` blindly, since the tree may hold unrelated in-progress work.
