---
name: surface-docs-drift
description: "Multi-agent workflow that reads the shipped product surfaces (API, CLI, SDK, UI, config parsers) across the amika and amika-mono repos and diffs them against the public docs, surfacing undocumented features and doc-vs-code contradictions. Fans out one reader per surface, then ranks the merged findings: contradictions, then shipped-but-undocumented, then partial."
argument-hint: "[surface...]"
---

# Surface docs drift

Run periodically (monthly) and before a release to surface undocumented features and doc-vs-code contradictions.

**Usage:** `/surface-docs-drift [surface...]` — `surface` is one or more of `api`, `cli`, `sdk`, `ui`, `config` (default: all five).

Subagents read only and report findings — they don't edit docs or file tickets.

## Repo paths

Resolve from configured working directories: **amika** (ends in `/amika`), **amika-mono**, and **docs** (current repo).

Check which repos the requested surfaces actually need:
- `api`, `ui`: amika-mono only
- `cli`, `sdk`: amika only
- `config`: both

If a required repo is missing, report which surfaces will be skipped and stop.

---

## Phase 1: Fan out one reader per surface

Spawn one Sonnet sub-agent per requested surface in parallel. Give each the entry paths below; no exploration outside them:

| Surface | Repo | Entry paths |
|---|---|---|
| `api` | amika-mono | `js/coding-agents/src/server/v0beta1/*` (route groups: `sandboxes`, `snapshots`, `sandbox-snapshots`, `secrets`, `api-keys`, `slack`, `docker-registries`, `services`, `integrations`, `storage`, `config`, `repositories`, `git-user-settings`) plus `js/coding-agents/src/server/openapi` |
| `cli` | amika | `go/cmd/amika/*.go` (each file is roughly one command group: `sandbox.go`, `snapshot.go`, `secrets.go`, `service.go`, `volume.go`, `auth.go`, `materialize.go`, etc.) |
| `sdk` | amika | `sdk/typescript/src/*` (`client.ts`, `http.ts`, `token.ts`, `types.ts`, `errors.ts`, `index.ts`) |
| `ui` | amika-mono | `js/coding-agents/src/app/(dashboard)/*` (`organization`, `settings`, `repositories`, `integrations`, `docker-registries`, `sandbox`) |
| `config` | both | Go parser (amika): `go/internal/amikaconfig/config.go`; TS parser (amika-mono): `js/coding-agents/src/lib/repositories/repo-config/toml/*` |

Brief each subagent to:

1. Enumerate the surface's real capabilities (`api`: routes/methods; `cli`: commands/flags; `sdk`: exported methods/types; `ui`: pages/actions; `config`: keys/sections — note Go/TS parser divergence, those gaps are findings too).
2. Grep the full docs tree (all `*.mdx` files including root-level pages, plus `docs.json`) for coverage of each capability.
3. Return a per-item table: capability, evidence (file:line in source), doc status (**Contradicted** / **Undocumented** / **Partial** / **Covered**), and the doc file:line if any exists.

## Phase 2: Merge and dedupe

Collect all reports. Dedupe across surfaces — a feature can be shipped in the UI and the API but missing from the SDK; that's one finding with multiple surface evidence, not three.

## Phase 3: Rank

Order the merged findings:

1. **Contradictions** — docs assert something false (e.g., "captured from the web UI" when the CLI and API both support it; "no DELETE endpoint" when one exists).
2. **Shipped but fully undocumented** — a real, working capability with zero doc mention.
3. **Partial** — documented, but thinner than the real surface (missing a flag, an endpoint variant, a config key).

Within each tier, prefer findings with the cleanest fix shape (a single doc page, a single missing table row) and call them out.

## Phase 4: Report

Emit the ranked list with, for each item: what's shipped (source evidence), what the docs say (or don't), and the fix location. Note Go vs. TS config-parser divergence separately — these are product bugs, not just doc gaps. Do not edit docs or file tickets.
