#!/bin/bash
set -e

# Install Mintlify CLI globally so `mintlify` is available
npm install -g mintlify@latest

# Start the Mintlify dev server in the background on port 3000
cd /home/amika/workspace/docs
mkdir -p /var/log/amika
nohup mintlify dev --port 3000 > /var/log/amika/mintlify.log 2>&1 &
