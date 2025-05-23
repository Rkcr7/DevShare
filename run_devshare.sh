#!/bin/bash

echo "Starting DevShare..."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

python main.py

echo "Application closed."
read -p "Press Enter to continue..." 