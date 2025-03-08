#!/bin/bash

# Navigate to the project root (assuming script is placed in INF_2900_TEAM5 folder)
cd "../$(dirname "$0")"

# Activate the virtual environment
python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
# Navigate to the library_manager directory
cd library_manager

# Run database migrations (optional, you can comment these out if migrations are not needed every time)
echo "Running database migrations..."
sudo service mysql start
python manage.py makemigrations
python manage.py migrate

# Start the Django development server
echo "Starting Django backend server..."
python manage.py runserver