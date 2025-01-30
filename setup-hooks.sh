#!/bin/sh

# Set the hooks path to the .githooks directory
git config core.hooksPath .githooks

# Make sure hooks are executable
chmod +x .githooks/*

echo "Git hooks have been set up successfully!"