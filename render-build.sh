#!/bin/bash

# Simple build script for Render deployment
# This script sets up environment and installs dependencies

set -e

echo "Starting Render build process..."

# Set Cargo environment variables to avoid read-only filesystem issues
export CARGO_HOME=/tmp/cargo
export CARGO_TARGET_DIR=/tmp/cargo-target
export CARGO_BUILD_TARGET_DIR=/tmp/cargo-target
export RUST_BACKTRACE=1

# Create directories
mkdir -p $CARGO_HOME
mkdir -p $CARGO_TARGET_DIR

echo "Cargo environment configured:"
echo "CARGO_HOME: $CARGO_HOME"
echo "CARGO_TARGET_DIR: $CARGO_TARGET_DIR"

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies with specific flags to prefer wheels
echo "Installing Python dependencies..."
pip install --only-binary=all --prefer-binary -r requirements.txt

echo "Build completed successfully!"
