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
