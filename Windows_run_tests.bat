@echo off
echo Activating Virtual Environment...
call venv\Scripts\activate
@REM python run_tests.py
cd %~dp0
cd library_manager
python manage.py test

echo Setting PYTHONPATH to include venv's site-packages...
set PYTHONPATH=%VIRTUAL_ENV%\Lib\site-packages;%PYTHONPATH%
echo.


echo Starting all tests...
%VIRTUAL_ENV%\Scripts\python run_tests.py  REM Execute run_tests.py from library_manager directory
pause 