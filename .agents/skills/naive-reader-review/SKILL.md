---
name: naive-reader-review
description: "Pressure-test a docs page or section by having a naive sub-agent read it cold, with no prior context. Spawns one Sonnet sub-agent per page that answers what the feature does, when you'd use it, what it assumed you already knew, and where it expected to find this but didn't. The supervisor then collates cross-page issues — discoverability, flow, placement, duplicated content — and proposes fixes."
argument-hint: "<page-or-section-path>"
---

# Naive reader review

Use when you want to know whether a docs page (or a whole section) actually works for a reader who has no context beyond what's on the page — no tribal knowledge of Amika's terminology, no memory of where things live in the nav.

**Usage:** `/naive-reader-review <page-or-section-path>`

- `page-or-section-path` (required): an `.mdx` file, or a directory (e.g. `guides/`, `reference/sandboxes/`) treated as a section — every `.mdx` page under it in scope.

---

## Phase 1: Resolve scope

If the path is a single file, scope is that one page. If it's a directory, scope is every `.mdx` page under it (recurse). List the resolved pages before continuing so the user can see what's in scope.

## Phase 2: Spawn one naive reader per page

For each page in scope, spawn a sub-agent with the Agent tool:

- `subagent_type: general-purpose`
- `model: sonnet`
- Point it at exactly one page. Tell it to read only that file: no exploring the rest of the docs repo, no following links, no outside knowledge of Amika, no charitable assumptions. It should answer only from the literal words on the page.

Brief it to act as a blunt, impatient, slightly dim first-time reader who will not fill in gaps, and to answer:

1. What does this feature do?
2. When would I use it?
3. What did this page assume I already knew — terms, prior steps, other pages — that it didn't explain?
4. Where did I expect to find this content but it wasn't there (a heading I looked for, a step that seemed to be missing)?

Ask it to flag any term it can't define from the page alone, and to keep the answer short. Run all readers in parallel — they're independent.

## Phase 3: Collate across pages

Read every sub-agent's answers. A single-page reader can't see cross-page problems; that's the supervisor's job. Look for:

- **Discoverability** — a reader repeatedly says they'd expect to find X here but don't; check whether X exists elsewhere in the docs and isn't linked from here.
- **Flow** — the assumed-prior-knowledge answers reveal a missing prerequisite step or an out-of-order section.
- **Placement** — a page's content would serve a reader better under a different nav tab/group (compare against `docs.json`'s actual structure, not what `AGENTS.md` claims it is — verify current tabs directly).
- **Inconsistent duplication** — the same mechanic (e.g. a config block, a setup step) explained slightly differently across two or more pages in scope; each version drifts a little from the others.

## Phase 4: Propose fixes

For each cross-page issue, propose a concrete fix: link to add, section to move, duplicated content to consolidate into one canonical page (with the others pointing to it), or a missing page/section to write. Name exact file paths and, where useful, a line or heading to anchor the change.

Present the proposed fixes to the user before editing anything — this skill's job is to diagnose and propose, not to silently rewrite pages out from under a reviewer. If the user confirms, make the edits following the docs repo's style (`AGENTS.md`) and conventions from the `mintlify` skill.

## Notes

- Run one reader per page even within a small section — cross-page comparison only works if each reader's take is uncontaminated by the others.
- The point is a cold reader's confusion, not prose polish. Don't let a proposed fix balloon a page's length just to cover every gap a naive reader found.
