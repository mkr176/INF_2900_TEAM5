@echo off
echo Activating Virtual Environment...
call venv\Scripts\activate
@REM python run_tests.py
cd %~dp0
cd library_manager
python manage.py test

pause 