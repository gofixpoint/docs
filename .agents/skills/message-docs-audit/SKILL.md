---
name: message-docs-audit
description: "Take a customer-facing message (email, launch post, blurb) as ground truth, extract every discrete product claim it makes, and check each against the public docs: Covered, Partial, Missing, or Contradicted. Also verifies every link in the message resolves. Emits a ranked report, contradictions first."
argument-hint: "<path-to-message>"
---

# Message docs audit

Use before sending a launch post, a feature-announcement email, or a design-partner update — anytime a message asserts product behavior to a customer and you want the docs to back it up.

**Usage:** `/message-docs-audit <path-to-message>`

- `path-to-message` (required): the source message. Treat it as ground truth — this skill checks the docs against the message, not the other way around.

---

## Phase 1: Extract claims

Read the message in full. Pull out a numbered list of discrete, checkable product claims: a feature exists, a command works a certain way, a config key has a given syntax, a URL points somewhere specific. Drop anything that isn't a product claim — scheduling, pleasantries, pricing/legal language outside doc scope.

Keep each claim to one checkable assertion. Split compound sentences ("snapshots are captured from the CLI and the web UI" is two claims) so each gets its own verdict.

## Phase 2: Check each claim against the docs

For each claim, grep and read the docs repo (you're running from it — the working directory is the docs root) for supporting text. Classify:

- **Covered** — docs state it, and accurately.
- **Partial** — docs mention it but thinner, or slightly off from the claim's wording.
- **Missing** — docs say nothing about it.
- **Contradicted** — docs state the opposite. Flag these loudest; they're the ones that get a customer hurt.

Record, for every claim, the exact doc file and line (or "no match found") backing the verdict.

## Phase 3: Verify links

Resolve every URL in the message. For internal doc links, confirm the page exists and any `#anchor` matches a real heading. For external links (app.amika.dev, GitHub, Discord), issue an HTTP HEAD or GET request (`curl -s -o /dev/null -w "%{http_code}" --max-time 10 <url>`) and flag any non-2xx or connection-failure responses as broken. Also flag anything that looks like it points to two different targets for the same thing (e.g. two different API-doc URLs for what should be one canonical page).

## Phase 4: Optional fan-out

For a short message (a handful of claims), do phases 1–3 yourself. For a long one (a full launch post or a multi-feature email with 20+ claims), split the claim list into clusters and spawn one Sonnet sub-agent per cluster to do Phase 2 checking, each returning verdicts with file/line evidence. Collate their results yourself before ranking — don't skip the synthesis step just because the checking was parallelized.

## Phase 5: Report

Emit a ranked report:

1. **Contradicted** claims first, each with the message's wording, the doc's contradicting text, and the file/line.
2. **Missing** claims next.
3. **Partial** claims last.

For each entry, name the exact page (and, if it exists, the line) where the fix should land. Skip a "Covered" section in the main report — a one-line count at the end is enough ("14 of 22 claims covered").

Do not edit any docs yourself. This skill only reports; fixing the gaps is a separate, human-reviewed step.
