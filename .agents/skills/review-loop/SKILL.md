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
2. Base branch: if an open PR exists, prefer its `baseRefName` (handles stacked PRs correctly):
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

Spawn a background `general-purpose` subagent to watch CI without blocking the loop. Brief it to:

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

Derive `<owner>`/`<repo>` from `gh repo view --json owner,name`. Page through all threads: on the first call pass `-F cursor=null` (use `-F` not `-f` — `-f` sends the string `"null"`, an invalid cursor), then re-run with `-F cursor=<endCursor>` while `pageInfo.hasNextPage` is true.

For **each thread where `isResolved` is false**, decide one of:

- **Fix**: the comment is valid. Make the code change.
- **Ignore/disagree**: irrelevant, out of scope, or you disagree. Do not change code.

Then **reply on the thread** via `gh` explaining the action, and resolve threads you fixed:

- Reply: `gh api repos/<owner>/<repo>/pulls/<number>/comments/<comment-databaseId>/replies -f body='<reply>'`
  - Use the **top-level comment's** `databaseId` (first in `comments.nodes`) — the reply endpoint rejects non-root comment ids.
  - For fixes: briefly state what you changed. For disagree/ignore: briefly state why.
- Resolve a thread you fixed:
  ```bash
  gh api graphql -f query='mutation($id:ID!){ resolveReviewThread(input:{threadId:$id}){ thread{ isResolved } } }' -f id=<threadId>
  ```
  Do **not** resolve threads you disagreed with; leave them open for the human reviewer.

Commit the comment-driven fixes with a clear message (see Commit conventions below). One commit for this batch is fine.

## Step 2: Review loop (always runs)

Loop up to **3 times**. Track a round counter.

### 2a: Spawn a reviewer subagent

Spawn a fresh `Explore` (read-only) subagent each round. Use `Explore`, not `general-purpose` — it has no `Edit`/`Write` tools, preventing accidental mutations. Brief it to:

- Review the branch diff against the base: `git diff <base>...HEAD` and read the changed files in full for context.
- Look for: correctness bugs, logic errors, missing error handling, security issues, broken tests, and violations of the `CLAUDE.md` conventions (e.g. no emdashes, module organization).
- Run available checks it can (typecheck/lint/tests for the affected package per that package's `AGENTS.md`) and report failures.
- Return a structured list of findings (file:line, severity, description, suggested fix), or an empty list if nothing is wrong.

**Guard:** capture `git status --short` before applying fixes. After the reviewer returns, confirm the tree is clean. For any stray edits: `git checkout -- <file>` is safe only if that file was clean at Step 0; if it had pre-existing changes, leave it alone and surface the issue to the user.

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

Follow `CLAUDE.md`: imperative subject, capitalized, ~50 chars; 72-char body; no AI attribution; no emdashes; stage only changed files (not `git add -A`).
