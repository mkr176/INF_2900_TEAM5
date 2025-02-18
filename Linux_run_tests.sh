#!/bin/bash

# Navigate to the project root (assuming script is placed in INF_2900_TEAM5 folder)
cd "$(dirname "$0")"

# Activate the virtual environment
python3 -m venv venv
source venv/bin/activate
echo "Running tests..."
python run_tests.py