@echo off
echo Starting DevShare...

REM Activate virtual environment if it exists
if exist venv (
    call venv\Scripts\activate
)

python main.py

echo Application closed.
pause 