#!/usr/bin/env bash

set -euo pipefail  # Enable strict error handling

# Function to log messages
log() {
    echo "[INFO] $1"
}

# Install apt packages if the list exists
if [ -f "apt-packages.txt" ]; then
    log "Installing apt packages from apt-packages.txt..."
    sudo apt-get update -y
    xargs -a apt-packages.txt sudo apt-get install -y
else
    log "No apt-packages.txt file found. Skipping apt package installation."
fi

# Upgrade pip and install Python dependencies
if [ -f "requirements.txt" ]; then
    log "Upgrading pip and installing Python dependencies from requirements.txt..."
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
else
    log "No requirements.txt file found. Skipping Python dependency installation."
fi

log "Post-create script completed successfully."
