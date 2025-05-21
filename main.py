"""
Screenshot Manager Main Module
This script runs the Screenshot Manager application, connecting the Telegram bot
with the UI and handling screenshots sent from your phone.
"""

import os
import signal
import sys

from modules.telegram_bot import TelegramBot
from modules.ui import ScreenshotUI
from modules.utils import load_history

def signal_handler(sig, frame):
    """Handle Ctrl+C to properly clean up resources."""
    print("Shutting down...")
    if 'bot' in globals() and bot:
        bot.stop()
    if 'ui' in globals() and ui:
        ui.stop()
    sys.exit(0)

def main():
    # Register signal handler for clean shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    # Create screenshot directory if it doesn't exist
    os.makedirs('./screenshots', exist_ok=True)
    
    # Initialize history
    history = load_history()
    
    # Create the Telegram bot
    bot = TelegramBot()
    bot.set_history(history)
    
    # Create and start the UI
    ui = ScreenshotUI(bot)
    
    # Start the bot
    bot.start()
    
    try:
        # Run the UI (this blocks until the UI is closed)
        ui.run()
    except Exception as e:
        print(f"Error in UI: {e}")
    finally:
        # Clean up when the UI is closed
        print("UI closed, shutting down application...")
        bot.stop()
        # Exit the program to ensure everything is properly closed
        sys.exit(0)
    
if __name__ == "__main__":
    main() 