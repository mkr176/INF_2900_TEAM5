@echo off
echo Starting all services...

REM --- Virtual Environment Setup ---
echo Checking for Virtual Environment...
if not exist venv (
    echo Virtual environment not found. Creating venv...
    python -m venv venv
    cd library_manager\frontend
    echo Installing npm dependencies...
    npm install
    cd ..
    cd ..

    if errorlevel 1 (
        echo Error creating virtual environment. Please ensure Python is installed and in your PATH.
        pause
        exit /b 1
    )
    echo Virtual environment created successfully.
)

echo Activating Virtual Environment...
call venv\Scripts\activate
if errorlevel 1 (
    echo Error activating virtual environment. Please check venv\Scripts\activate.
    pause
    exit /b 1
)

REM --- Dependency Installation ---
echo Installing dependencies from requirements.txt...
pip install -r requirements.txt
if errorlevel 1 (
    echo Error installing dependencies. Please check requirements.txt and pip output.
    pause
    exit /b %errorlevel%
)
echo Dependencies installed successfully.

REM --- Starting Services and Tests ---
echo Starting Backend, Frontend, and Tests...

echo Starting Backend in a new window...
start cmd /k "call Windows_start_backend.bat"

echo Starting Frontend in a new window...
start cmd /k "call Windows_start_frontend.bat"

REM --- Open Browser ---
echo Opening browser to http://localhost:8000...
start http://localhost:8000/

echo Running Tests in this window...
call Windows_run_tests.bat

echo All services started and tests executed. Please check separate command prompt windows for backend and frontend, and this window for test results.
pause
    