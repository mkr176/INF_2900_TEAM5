@echo off
echo Starting all services...

echo Activating Virtual Environment...
call venv\Scripts\activate

echo Starting Backend in a new window...
start cmd /k "echo Starting Django Backend Server... && cd library_manager && python manage.py makemigrations && python manage.py migrate && python manage.py runserver"

echo Starting Frontend in a new window...
start cmd /k "echo Starting React Frontend Server... && cd library_manager\frontend && npm run dev"

echo Running Tests in this window...
@REM echo Navigating to root directory for tests...
cd %~dp0
cd library_manager
python manage.py test

@REM python run_tests.py
pause

echo All services started. Please check separate command prompt windows for backend and frontend, and this window for test results.

    