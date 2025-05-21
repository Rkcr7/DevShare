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

def get_screenshot_path(timestamp):
    """Get path for a screenshot with given timestamp."""
    # Replace colons and other characters that might not be suitable for filenames
    safe_timestamp = timestamp.replace(":", "-")
    return os.path.join(SCREENSHOT_DIR, f"screenshot_{safe_timestamp}.png") 