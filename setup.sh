#!/bin/bash

echo "============================================"
echo "Screenshot Manager - Easy Setup"
echo "============================================"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python is not installed or not in your PATH"
    echo "Please install Python 3 using your package manager:"
    echo "Ubuntu/Debian: sudo apt install python3 python3-pip python3-venv"
    echo "macOS: brew install python3"
    echo
    exit 1
fi

# Check Python version
PYVER=$(python3 --version | cut -d" " -f2)
echo "Found Python $PYVER"

# Create virtual environment (optional but recommended)
echo
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "Failed to create virtual environment"
        echo "Installing directly to system Python..."
    else
        echo "Virtual environment created successfully"
    fi
else
    echo "Virtual environment already exists"
fi

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Install dependencies
echo
echo "Installing required packages..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Failed to install some dependencies. Trying alternative method..."
    pip uninstall -y python-telegram-bot urllib3
    pip install -r requirements.txt
fi

# Install platform-specific dependencies
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo
    echo "Installing Linux-specific dependencies..."
    if command -v apt-get &> /dev/null; then
        echo "Detected apt package manager. Installing xclip..."
        sudo apt-get install -y xclip
    elif command -v dnf &> /dev/null; then
        echo "Detected dnf package manager. Installing xclip..."
        sudo dnf install -y xclip
    elif command -v pacman &> /dev/null; then
        echo "Detected pacman package manager. Installing xclip..."
        sudo pacman -S --noconfirm xclip
    else
        echo "Unable to detect package manager. Please install xclip manually."
    fi
fi

# Create screenshots directory
if [ ! -d "screenshots" ]; then
    echo "Creating screenshots directory..."
    mkdir screenshots
fi

# Check if config.json exists, if not, run the setup wizard
if [ ! -f "config.json" ]; then
    echo "First-time setup: Running setup wizard..."
    python -c "from modules.setup_wizard import SetupWizard; wizard = SetupWizard(); wizard.show()"
fi

echo
echo "============================================"
echo "Setup complete! You can now run the application with:"
echo "bash run_screenshot_manager.sh"
echo "============================================"

read -p "Press Enter to continue..." 