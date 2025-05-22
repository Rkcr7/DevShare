import os
import json
import hashlib
from datetime import datetime

# Define constants
SCREENSHOT_DIR = './screenshots'
HISTORY_FILE = './screenshots.json'
RECENT_HASHES = 5  # Number of recent hashes for de-duplication
THUMBNAIL_SIZE = (50, 50)  # Thumbnail dimensions for UI

# Ensure directories and files exist
os.makedirs(SCREENSHOT_DIR, exist_ok=True)
if not os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, 'w') as f:
        json.dump([], f)

# Load history
def load_history():
    """Load screenshot history from file."""
    with open(HISTORY_FILE, 'r') as f:
        return json.load(f)

# Save history
def save_history(history):
    """Save screenshot history to file."""
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f)

def calculate_hash(file_path):
    """Calculate MD5 hash of a file."""
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        hasher.update(f.read())
    return hasher.hexdigest()

def generate_timestamp():
    """Generate a timestamp for filename in dd-mm-yyyy---HH:MM:SS format."""
    return datetime.now().strftime("%d-%m-%Y---%H:%M:%S")

def get_screenshot_path(timestamp, file_extension="png"):
    """Get a unique path for a screenshot with given timestamp and extension."""
    # Timestamp is now expected to be in format dd-mm-yyyy---HH-MM-SS-ffffff
    # No need to replace colons as they should already be hyphens or not present in critical parts.
    base_filename = f"screenshot_{timestamp}"
    file_path = os.path.join(SCREENSHOT_DIR, f"{base_filename}.{file_extension}")
    
    # Handle potential collisions by appending a counter
    counter = 1
    while os.path.exists(file_path):
        file_path = os.path.join(SCREENSHOT_DIR, f"{base_filename}_{counter}.{file_extension}")
        counter += 1
    return file_path 