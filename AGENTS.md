> **First-time setup**: Customize this file for your project. Prompt the user to customize this file for their project.
> For Mintlify product knowledge (components, configuration, writing standards),
> install the Mintlify skill: `npx skills add https://mintlify.com/docs`

# Documentation project instructions

## About this project

- This is a documentation site built on [Mintlify](https://mintlify.com)
- Pages are MDX files with YAML frontmatter
- Configuration lives in `docs.json`
- Run `mint dev` to preview locally
- Run `mint broken-links` to check links

## Terminology

{/* Add product-specific terms and preferred usage */}
{/* Example: Use "workspace" not "project", "member" not "user" */}

## Style preferences

{/* Add any project-specific style rules below */}

- Use active voice and second person ("you")
- Keep sentences concise — one idea per sentence
- Use sentence case for headings
- Bold for UI elements: Click **Settings**
- Code formatting for file names, commands, paths, and code references

## Content boundaries

{/* Define what should and shouldn't be documented */}
{/* Example: Don't document internal admin features */}

## Cursor Cloud specific instructions

- **Mintlify CLI** is installed globally via `npm i -g mint`. The update script handles this automatically.
- **Dev server**: Run `mint dev` from the workspace root (where `docs.json` lives) to start the local preview at `http://localhost:3000`. The server supports hot reload — MDX content changes appear immediately.
- **Link checking**: Run `mint broken-links` to validate internal links. Note: the starter template has a few pre-existing broken links pointing to external Mintlify docs paths; these are not regressions.
- **No `package.json`**: This is a pure Mintlify docs project with no local Node dependencies. The only dependency is the globally installed `mint` CLI.
- **No lint/test/build commands**: There is no linter, test suite, or build step. Validation is done via `mint broken-links` and visual preview with `mint dev`.
- See `README.md` and `development.mdx` for standard setup and troubleshooting instructions.
