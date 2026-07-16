---
name: message-docs-audit
description: "Extract product claims from a customer-facing message and verify each against the docs: Covered, Partial, Missing, or Contradicted. Also verifies every link resolves. Emits a ranked report, contradictions first."
argument-hint: "<path-to-message>"
---

# Message docs audit

**Usage:** `/message-docs-audit <path-to-message>`

- `path-to-message` (required): the source message. Treat it as ground truth — this skill checks the docs against the message, not the other way around.

---

## Phase 1: Extract claims

Extract a numbered list of discrete product claims (features, commands, config syntax, specific URLs). Drop non-claims: scheduling, pleasantries, pricing/legal.

Keep each claim to one checkable assertion. Split compound sentences ("snapshots are captured from the CLI and the web UI" is two claims) so each gets its own verdict.

## Phase 2: Check each claim against the docs

For each claim, grep the docs for supporting text. Classify:

- **Covered** — docs state it accurately.
- **Partial** — docs mention it but thinner, or slightly off from the claim's wording.
- **Missing** — docs say nothing about it.
- **Contradicted** — docs state the opposite.

Record, for every claim, the exact doc file and line (or "no match found") backing the verdict.

## Phase 3: Verify links

Resolve every URL in the message. For internal doc links, confirm the page exists and any `#anchor` matches a real heading. For external links (e.g., app.amika.dev, github.com, discord.gg), issue an HTTP request with redirect-following (`curl -sL -o /dev/null -w "%{http_code}" --max-time 10 <url>`) and flag any non-2xx final response or connection-failure as broken. Also flag anything that looks like it points to two different targets for the same thing (e.g. two different API-doc URLs for what should be one canonical page).

## Phase 4: Optional fan-out

For short messages, do phases 1–3 yourself. For long ones (20+ claims), fan out Phase 2 to one Sonnet sub-agent per claim cluster, then collate and rank their results yourself.

## Phase 5: Report

Rank and report:

1. **Contradicted** claims first, each with the message's wording, the doc's contradicting text, and the file/line.
2. **Missing** claims next.
3. **Partial** claims last.

For each entry, name the exact page (and, if it exists, the line) where the fix should land. Skip a "Covered" section in the main report — a one-line count at the end is enough ("14 of 22 claims covered").
