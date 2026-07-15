---
name: surface-docs-drift
description: "Multi-agent workflow that reads the shipped product surfaces (API, CLI, SDK, UI, config parsers) across the amika and amika-mono repos and diffs them against the public docs, surfacing undocumented features and doc-vs-code contradictions. Fans out one reader per surface, then ranks the merged findings: contradictions, then shipped-but-undocumented, then partial."
argument-hint: "[surface...]"
---

# Surface docs drift

Reads product source to police the docs. Run periodically (monthly) and before a release — the natural sibling to `/changelog`: changelog says what shipped, this says what shipped *and never got documented*.

**Usage:** `/surface-docs-drift [surface...]`

- `surface` (optional): one or more of `api`, `cli`, `sdk`, `ui`, `config`. If omitted, run all five.

This skill reads product source, not just docs. Subagents read only — they never write to the amika or amika-mono repos, and they don't edit docs either; this skill reports, it doesn't fix.

## Repo paths

Resolve repo roots the same way `/changelog` does: from the additional working directories configured in Claude Code.

- **amika**: the directory ending in `/amika` (not `amika-mono`)
- **amika-mono**: the directory ending in `/amika-mono`
- **docs**: the repo you're already running in

If `amika` or `amika-mono` is missing from your working directories, tell the user and stop — you can't diff against source you can't read.

---

## Phase 1: Fan out one reader per surface

Spawn a Sonnet sub-agent per requested surface (all five by default) with the Agent tool, run in parallel. Give each one the exact entry paths below and nothing else to explore outside them (they can follow imports within the surface, but shouldn't wander into unrelated parts of the repo):

| Surface | Repo | Entry paths |
|---|---|---|
| `api` | amika-mono | `js/coding-agents/src/server/v0beta1/*` (route groups: `sandboxes`, `snapshots`, `sandbox-snapshots`, `secrets`, `api-keys`, `slack`, `docker-registries`, `services`, `integrations`, `storage`, `config`, `repositories`, `git-user-settings`) plus `js/coding-agents/src/server/openapi` |
| `cli` | amika | `go/cmd/amika/*.go` (each file is roughly one command group: `sandbox.go`, `snapshot.go`, `secrets.go`, `service.go`, `volume.go`, `auth.go`, `materialize.go`, etc.) |
| `sdk` | amika | `sdk/typescript/src/*` (`client.ts`, `http.ts`, `token.ts`, `types.ts`, `errors.ts`, `index.ts`) |
| `ui` | amika-mono | `js/coding-agents/src/app/(dashboard)/*` (`organization`, `settings`, `repositories`, `integrations`, `docker-registries`, `sandbox`) |
| `config` | both | Go parser: `amika/go/internal/amikaconfig/config.go`; TS parser: `amika-mono/js/coding-agents/src/lib/repositories/repo-config/toml/*` |

Brief each subagent to:

1. Enumerate the surface's real, current capabilities: for `api`, every route/method; for `cli`, every command/subcommand/flag; for `sdk`, every exported method/type; for `ui`, every page/major user-facing action; for `config`, every recognized key/section (note where the two parsers diverge — Go and TS should stay in sync, and gaps between them are themselves a finding).
2. For each capability, grep the docs repo (`docs.json`, `guides/`, `reference/`, `sdks/`, `architecture/`) for matching coverage.
3. Return a per-item table: capability, evidence (file:line in source), doc status (**Contradicted** / **Undocumented** / **Partial** / **Covered**), and the doc file:line if any exists.

## Phase 2: Merge and dedupe

Collect all five (or requested) reports. Dedupe across surfaces — a feature can be shipped in the UI and the API but missing from the SDK; that's one finding with multiple surface evidence, not three.

## Phase 3: Rank

Order the merged findings:

1. **Contradictions** — docs assert something false (e.g., "captured from the web UI" when the CLI and API both support it; "no DELETE endpoint" when one exists).
2. **Shipped but fully undocumented** — a real, working capability with zero doc mention.
3. **Partial** — documented, but thinner than the real surface (missing a flag, an endpoint variant, a config key).

Within each tier, prefer findings with the cleanest fix shape (a single doc page, a single missing table row) over sprawling ones, and call out clean-fix candidates explicitly so they can be picked off first.

## Phase 4: Report

Emit the ranked list with, for each item: what's shipped (source evidence), what the docs currently say (or don't), and the exact doc page the fix belongs on. Note any config-parser divergence (Go vs. TS) separately, since that's a product bug candidate, not just a docs gap. Do not edit docs or file tickets — hand the report back for a human to act on or turn into doc tickets.
