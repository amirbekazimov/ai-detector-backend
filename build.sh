#!/bin/bash

# Build script for Render deployment
# This script sets up the proper environment for Rust/Cargo compilation

set -e

echo "Setting up Cargo environment for Render deployment..."

# Set Cargo environment variables to use writable directories
export CARGO_HOME=/tmp/cargo
export CARGO_TARGET_DIR=/tmp/cargo-target
export CARGO_BUILD_TARGET_DIR=/tmp/cargo-target
export RUST_BACKTRACE=1

# Create directories if they don't exist
mkdir -p $CARGO_HOME
mkdir -p $CARGO_TARGET_DIR

echo "Cargo environment configured:"
echo "CARGO_HOME: $CARGO_HOME"
echo "CARGO_TARGET_DIR: $CARGO_TARGET_DIR"

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Build completed successfully!"
