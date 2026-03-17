# Cursor Cloud specific instructions

- **Mintlify CLI** is installed globally via `npm i -g mint`. The update script handles this automatically.
- **Dev server**: Run `mint dev` from the workspace root (where `docs.json` lives) to start the local preview at `http://localhost:3000`. The server supports hot reload — MDX content changes appear immediately.
- **Link checking**: Run `mint broken-links` to validate internal links. Note: the starter template has a few pre-existing broken links pointing to external Mintlify docs paths; these are not regressions.
- **No `package.json`**: This is a pure Mintlify docs project with no local Node dependencies. The only dependency is the globally installed `mint` CLI.
- **No lint/test/build commands**: There is no linter, test suite, or build step. Validation is done via `mint broken-links` and visual preview with `mint dev`.
- See `README.md` for standard setup instructions.
