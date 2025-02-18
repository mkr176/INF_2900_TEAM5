@echo off
echo Activating Virtual Environment...
call venv\Scripts\activate

python run_tests.py
pause 