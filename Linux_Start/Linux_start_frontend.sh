#!/bin/bash

# Navigate to the frontend directory (assuming script is placed in INF_2900_TEAM5 folder)
cd "../$(dirname "$0")/library_manager/frontend"

# Start the React development server
echo "Starting React frontend server..."
npm install
npm install framer-motion
npm run dev
