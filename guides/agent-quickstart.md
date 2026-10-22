---
title: "Agent quickstart"
description: "Instructions for a coding agent to set up and operate Amika."
---

## Start here

Send this prompt to your coding agent:

```markdown
Follow the instructions in https://docs.amika.dev/guides/agent-quickstart to set up and use Amika.
```

The rest of this page is written for the agent. You do not need to perform its
steps yourself.

## Instructions for the agent

To set up Amika, first make sure you either:

1. have an Amika API key
2. have installed and logged into the `amika` CLI (use `amika auth status` to check)

If you don't have either of the above, Your human can sign up at https://app.amika.dev/signup. Have them go through onboarding, and then report back.

### Offer to install the amika-cli skill

Do this once the `amika` CLI is installed and `amika auth status` shows you are
logged in. If you are working only with an API key and the CLI is not
installed, skip this step.

The amika-cli skill teaches coding agents the CLI's commands, which commands
block on interactive prompts, and how to get JSON output. `amika skill install`
installs the copy of the skill embedded in the CLI binary, so the skill matches
the installed CLI version.

1. Ask your human these two questions, then stop and wait for their answers:
   1. Install the amika-cli skill locally (this repo or project only), globally
      (every project on this machine), or not at all?
   2. Which agents should get it: Claude Code, Codex, Cursor, or several of
      them? Suggest the agent you are as the default. If you are none of these,
      ask without a default.
2. If they chose not at all, skip the rest of this step.
3. Otherwise, run `amika skill install` with the flags that match their answers:
   - `--local` for this repo or project only, or `--global` for every project.
     Pass exactly one.
   - `--agents` with a comma-separated list of `claude`, `codex`, and `cursor`.

   For example, to install the skill for Claude Code and Codex in every project:

   ```bash
   amika skill install --global --agents claude,codex
   ```

4. Tell your human which agents got the skill and whether it was installed
   locally or globally, including any paths the command reports.

### Learn how to operate Amika

Read these docs first:

- https://docs.amika.dev/
- https://docs.amika.dev/quickstart
- https://docs.amika.dev/install

To operate Amika, you can use either:

1. the `amika` CLI
   1. docs: https://docs.amika.dev/reference/cli
   2. implementation: https://github.com/gofixpoint/amika/tree/main/go/cmd/amika
2. the TypeScript SDK
   1. docs: https://docs.amika.dev/sdks/typescript/quickstart
   2. OSS implementation: https://github.com/gofixpoint/amika/tree/main/sdk/typescript
3. the raw HTTP API: https://app.amika.dev/api/docs and https://app.amika.dev/api/openapi.json
4. if you are a human, the UI at https://app.amika.dev/

The full docs are at https://docs.amika.dev/. In the docs, there are "Guides
for agents" which are agent specific. But you can read any docs pages that are
useful.

All OSS code is at https://github.com/gofixpoint/amika

If you are trying to connect your own machine as a sandbox host:
https://docs.amika.dev/guides/byoc
