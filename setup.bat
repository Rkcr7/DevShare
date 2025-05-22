@echo off
echo ============================================
echo Screenshot Manager - Easy Setup
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python is not installed or not in your PATH
    echo Please download and install Python from https://www.python.org/downloads/
    echo Ensure "Add Python to PATH" is checked during installation
    echo.
    pause
    exit /b 1
)

REM Check Python version
for /f "tokens=2" %%I in ('python --version 2^>^&1') do set pyver=%%I
echo Found Python %pyver%

REM Create virtual environment (optional but recommended)
echo.
echo Creating virtual environment...
if not exist venv (
    python -m venv venv
    if %ERRORLEVEL% NEQ 0 (
        echo Failed to create virtual environment
        echo Installing directly to system Python...
    ) else (
        echo Virtual environment created successfully
    )
) else (
    echo Virtual environment already exists
)

REM Activate virtual environment if it exists
if exist venv (
    echo Activating virtual environment...
    call venv\Scripts\activate
)

REM Install dependencies
echo.
echo Installing required packages...
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo Failed to install some dependencies. Trying alternative method...
    pip uninstall -y python-telegram-bot urllib3
    pip install -r requirements.txt
)

REM Create screenshots directory
if not exist screenshots (
    echo Creating screenshots directory...
    mkdir screenshots
)

REM Check if config.json exists, if not, run the setup wizard
if not exist config.json (
    echo First-time setup: Running setup wizard...
    python -c "from modules.setup_wizard import SetupWizard; wizard = SetupWizard(); wizard.show()"
)

echo.
echo ============================================
echo Setup complete! You can now run the application with run_screenshot_manager.bat
echo ============================================

pause 