# docs/ — agent context

Amika's public docs site, built with Mintlify and deployed to
docs.amika.dev.

## What this documents

Amika is a platform for managed coding-agent sandboxes. Developers
interact with it through three interfaces, all in scope for these docs:

- HTTP API and SDKs
- The `amika` CLI
- The web UI at app.amika.dev

All three default to the hosted platform. The CLI is open source and also
supports running sandboxes locally off-platform (`--local`); treat that as
an opt-in OSS mode, not a separate product. Design content for the
hosted-platform user first.

## Source repos

Amika's source lives in two repos that may or may not be present on disk.
If they are, they're typically siblings of this repo:

- `amika` (`../amika`) — Go CLI (`cmd/amika/`), OSS `amika-server`
  (`cmd/amika-server/`, `internal/httpapi/`), preset images, the
  `.amika/config.toml` CLI parser (`internal/amikaconfig/`), `ROADMAP.md`.
- `amika-mono` (`../amika-mono`) — Next.js webapp (`js/coding-agents/`),
  hosted API routes (`js/coding-agents/src/app/api/`), DB schema, the
  fuller `.amika/config.toml` parser
  (`js/coding-agents/src/lib/repositories/repo-config/toml/`), `specs/`.

Verify CLI flags, config keys, and API shapes against source before
documenting them. Don't invent.

## Navigation

`docs.json` defines three tabs:

- **Guides** — getting started, how-tos.
- **API and CLI Reference** — flag and config tables, endpoint lists.
- **Architecture** — system design, roadmap.

Placement rules:

- New how-to → Guides.
- New flag table or endpoint → Reference.
- New design direction → Architecture.
- Adding a page is a deliberate choice — prefer editing existing pages.
- Any new `.mdx` must be wired into `docs.json` to appear.

## Style

- Short, direct, concrete. Existing pages are the baseline.
- Active voice, second person ("you").
- Sentence case for headings. One idea per sentence.
- No emojis.
- Frontmatter: `title` + `description`.
- Bold for UI elements (Click **Settings**); code formatting for file
  names, commands, paths, and code references.
- Mintlify components in use: `<Note>`, `<Info>`, `<Tip>`, `<Warning>`,
  `<Steps>`/`<Step>`, `<CardGroup cols={N}>` + `<Card icon href>`,
  `<CodeGroup>`.
- Cross-link with bare paths like `/guides/services` — no `.mdx` suffix.
- Reusable content lives in `snippets/`. Mark a page as research preview by
  importing `/snippets/research-preview.mdx` at the top — not with an inline
  `<Note>` or a `tag: "Research preview"` frontmatter pill.

## Local workflow

- Run `./setup-repo.sh` once after cloning to install the git hooks
  (`core.hooksPath` → `githooks/`). The `pre-commit` hook runs
  `mint broken-links`; it skips with a warning if `mint` isn't installed.
- `mint dev` from the repo root to preview at `http://localhost:3000`
  (hot reload).
- `mint broken-links` to validate internal links.
- No `package.json`, no lint or test suite — validation is preview plus
  link check.

## Stable external URLs

- Install script: https://raw.githubusercontent.com/gofixpoint/amika/main/install.sh
- Hosted platform: https://app.amika.dev
- GitHub: https://github.com/gofixpoint/amika
- Discord: https://discord.gg/xDXk4KjGWg

## Cursor Cloud specific

See [AGENTS.cursor.md](AGENTS.cursor.md) for Cursor Cloud environment
details.
