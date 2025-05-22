"""
Screenshot Manager Main Module
This script runs the Screenshot Manager application, connecting to the cloud service
for handling screenshots sent from your phone via Telegram.
"""

import os
import signal
import sys
import json

from modules.ui import ScreenshotUI
from modules.cloud_service import CloudService
from modules.setup_wizard import SetupWizard
from modules.utils import load_history

def signal_handler(sig, frame):
    """Handle Ctrl+C to properly clean up resources."""
    print("Shutting down...")
    if 'cloud_service' in globals() and cloud_service:
        cloud_service.disconnect()
    if 'ui' in globals() and ui:
        ui.stop()
    sys.exit(0)

def check_first_run():
    """Check if this is the first run of the application"""
    config_file = './config.json'
    
    # If config file doesn't exist, it's first run
    if not os.path.exists(config_file):
        return True
    
    # If config file exists but is incomplete
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        if 'telegram_id' not in config or not config['telegram_id']:
            return True
            
        if 'service_url' not in config:
            return True
            
        return False
    except:
        return True

def run_setup_wizard():
    """Run the setup wizard and return configuration"""
    wizard = SetupWizard()
    wizard.show()
    
    # Load the saved config
    config_file = './config.json'
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            config = json.load(f)
        return config.get('telegram_id', ''), config.get('service_url', '')
    
    return None, None

def handle_new_screenshot(file_path, timestamp):
    """Handle new screenshots from the cloud service"""
    global ui
    
    # Update UI with new screenshot
    if ui:
        # Reload history
        history = load_history()
        ui.history = history
        
        # Update the UI - allowing cooldown to manage refresh rate
        ui.refresh_history()
        
        # Just update status without triggering another refresh
        ui.update_status(f"New screenshot received: {timestamp}")

def main():
    global cloud_service, ui
    
    # Register signal handler for clean shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    # Create screenshot directory if it doesn't exist
    os.makedirs('./screenshots', exist_ok=True)
    
    # Check if this is the first run
    if check_first_run():
        telegram_id, service_url = run_setup_wizard()
        if not telegram_id:
            print("Setup not completed. Exiting.")
            sys.exit(1)
    else:
        # Load config
        with open('./config.json', 'r') as f:
            config = json.load(f)
        telegram_id = config.get('telegram_id', '')
        service_url = config.get('service_url', '')
    
    # Connect to the cloud service
    cloud_service = CloudService(telegram_id, callback=handle_new_screenshot)
    if service_url:
        cloud_service.service_url = service_url
    
    # Initialize history
    history = load_history()
    
    # Create and start the UI
    ui = ScreenshotUI(None)  # No bot parameter, using cloud service instead
    
    # Connect to cloud service
    connected = cloud_service.connect()
    if connected:
        ui.update_status(f"Connected to cloud service. Ready for screenshots.")
    else:
        ui.update_status(f"Failed to connect to cloud service. Check your settings.")
    
    try:
        # Run the UI (this blocks until the UI is closed)
        ui.run()
    except Exception as e:
        print(f"Error in UI: {e}")
    finally:
        # Clean up when the UI is closed
        print("UI closed, shutting down application...")
        if cloud_service:
            cloud_service.disconnect()
        # Exit the program to ensure everything is properly closed
        sys.exit(0)
    
if __name__ == "__main__":
    cloud_service = None
    ui = None
    main() 