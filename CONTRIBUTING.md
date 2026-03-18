# Contributing

Thanks for helping improve the Amika docs!

## Quick start

1. Fork and clone this repository.
2. Create a branch for your changes.
3. Preview locally with `npx mintlify@latest dev`.
4. Commit your changes and open a pull request.

## Writing guidelines

- Use active voice: "Run the command" not "The command should be run".
- Address the reader directly with "you".
- Keep sentences concise — one idea per sentence.
- Include examples wherever possible.
- Use consistent terminology (don't alternate between synonyms).

## Syncing from source

Most docs content originates in the [amika](https://github.com/gofixpoint/amika) repo under `docs/`. When updating reference or guide pages, check the source docs for the latest content.

## File conventions

- All docs pages use `.mdx` extension.
- File names use kebab-case (e.g. `cli-reference.mdx`).
- New pages must be added to the `navigation` section in `docs.json` to appear on the site.
