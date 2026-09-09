#!/bin/bash
set -e

# This runs on initial setup and each hosted sandbox resume.
cd "$AMIKA_AGENT_CWD"
mkdir -p /var/log/amika
nohup mintlify dev --port 3000 > /var/log/amika/mintlify.log 2>&1 &
