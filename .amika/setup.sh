#!/bin/bash
set -e

# Install Mintlify CLI globally so `mintlify` is available
sudo npm install -g mintlify@latest

# Start the docs server on initial rig creation. start.sh also runs when a
# stopped hosted rig resumes; dependency installation stays here.
"$AMIKA_AGENT_CWD/.amika/start.sh"
