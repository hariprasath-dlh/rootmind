#!/usr/bin/env bash

# setup.sh - Environment Bootstrap Script
# Builds folders, validates Python version, creates virtualenv, and installs dependencies.

set -eo pipefail

echo "========================================="
echo "Initializing RootMind Project Setup..."
echo "========================================="

# 1. Check Python version
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is required but not installed." >&2
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "Detected Python version: $PYTHON_VERSION"

# 2. Create local directory mounts if not present
mkdir -p data/sample_logs
mkdir -p data/mock_codebase
mkdir -p data/test_datasets

# 3. Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment in venv/..."
    python3 -m venv venv
else
    echo "Virtual environment already exists."
fi

# 4. Activate and install requirements
echo "Installing requirements inside backend/..."
source venv/bin/activate || source venv/Scripts/activate
pip install --upgrade pip
pip install -r backend/requirements.txt

# 5. Populate initial env file if missing
if [ ! -f ".env" ]; then
    echo "Creating copy of .env.example into .env..."
    cp .env.example .env
fi

echo "========================================="
echo "Setup Complete! To start backend run:"
echo "source venv/bin/activate && uvicorn backend.app.main:app --reload"
echo "========================================="
