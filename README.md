# Amika Documentation

Source for the [Amika docs site](https://docs.amika.dev), built with [Mintlify](https://mintlify.com).

## Local development

Preview the docs locally:

```bash
npx mintlify@latest dev
```

The site will be available at `http://localhost:3000`.

## Deployment

Changes merged to `main` are deployed automatically via the Mintlify GitHub app.

## Project structure

- `docs.json` — site configuration (navigation, theme, metadata)
- `index.mdx` / `quickstart.mdx` — landing and getting-started pages
- `guides/` — how-to guides (sandbox config, presets, authentication)
- `reference/` — CLI and HTTP API reference
- `architecture/` — system design and roadmap
