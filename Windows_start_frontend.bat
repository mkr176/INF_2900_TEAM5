@echo off
echo Navigating to frontend directory...
cd library_manager\frontend

echo Starting React frontend server...
npm run dev
if %errorlevel% neq 0 (
    echo npm run dev failed (error code: %errorlevel%). Attempting to install npm dependencies...
    npm install
)

echo Frontend script execution finished.
pause