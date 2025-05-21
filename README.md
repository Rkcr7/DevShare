# Screenshot Manager

A powerful screenshot management system that:

1. Receives screenshots sent from your phone to a Telegram bot
2. Automatically copies them to your PC's clipboard for pasting anywhere
3. Provides a modern UI to manage screenshots with features like search, delete, history with thumbnails, notifications, and theme toggling

## Features

- **Security**: Only the authorized user (you) can use the bot
- **Modern UI**: Clean, modern interface with theme switching
- **Screenshot Management**: Search, delete, and re-copy screenshots
- **De-duplication**: Avoids duplicate screenshots
- **Cross-platform**: Works on Windows, macOS, and Linux
- **Configurable**: Adjustable polling interval, optional notifications
- **Thumbnails**: Shows image thumbnails alongside timestamps
- **Copy Buttons**: One-click copy buttons for each screenshot

## Prerequisites

- Python 3.6 or higher
- A Telegram account and the Telegram app on your phone
- Internet connection on both your phone and PC

## Installation

1. Clone or download this repository
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

If you encounter any dependency issues, try uninstalling and reinstalling the packages:

```bash
pip uninstall -y python-telegram-bot urllib3
pip install -r requirements.txt
```

3. For Linux users, install xclip for clipboard functionality:

```bash
sudo apt-get install xclip
```

## Configuration

The script is pre-configured with:
- Your Telegram bot token
- Your Telegram user ID

If you need to change these details, edit the following line in `modules/telegram_bot.py`:

```python
API_TOKEN = '7594536865:AAEX7CXhlQPy5v34fJqST-iTQh1x73xMN2U'  # Your bot's API token
AUTHORIZED_USER_ID = 860118391  # Your Telegram user ID
```

## Usage

1. Start the application:

```bash
python main.py
```

Or simply double-click `run_screenshot_manager.bat` on Windows.

2. Open Telegram on your phone, find your bot (@ritikrkcr7's bot), and start a chat.
3. Send `/start` to initialize the bot.
4. Send screenshots from your phone to the bot.
5. The screenshots will be automatically copied to your PC's clipboard.
6. Use the UI to manage, search, and re-copy your screenshots.

## Code Structure

The codebase is organized into modules for better maintainability:

- `main.py` - Main entry point that ties everything together
- `modules/telegram_bot.py` - Telegram bot functionality
- `modules/clipboard.py` - Cross-platform clipboard operations
- `modules/ui.py` - UI components and logic
- `modules/utils.py` - Utility functions for file handling

## Troubleshooting

- **Bot Doesn't Respond**: Ensure your internet connection is active and the script is running
- **Clipboard Not Working**: 
  - Windows: Verify pywin32 is installed
  - Linux: Ensure xclip is installed
  - macOS: No extra setup needed
- **UI Issues**: Make sure customtkinter is installed correctly
- **Dependency Errors**: If you see errors about missing modules like `urllib3.contrib.appengine`, run:
  ```bash
  pip uninstall -y python-telegram-bot urllib3
  pip install -r requirements.txt
  ``` 