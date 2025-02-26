#!/bin/bash

# Run backend script in the background
echo "Starting backend..."
bash Linux_start_backend.sh &

# Run frontend script in the background
echo "Starting frontend..."
bash Linux_start_frontend.sh &

# Run tests script in the foreground
echo "Running tests..."
bash Linux_run_tests.sh

echo "All scripts executed."