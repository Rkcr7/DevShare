from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
from plyer import notification
from modules.utils import calculate_hash, generate_timestamp, get_screenshot_path, save_history
from modules.clipboard import copy_to_clipboard

# Configuration
API_TOKEN = '7594536865:AAEX7CXhlQPy5v34fJqST-iTQh1x73xMN2U'
AUTHORIZED_USER_ID = 860118391

# Keep track of recent hashes to avoid duplicates
recent_hashes = []
MAX_RECENT_HASHES = 5

class TelegramBot:
    def __init__(self, update_ui_callback=None, notify_enabled=None):
        self.updater = None
        self.update_ui_callback = update_ui_callback
        # Use a regular boolean instead of tkinter BooleanVar, default to False (disabled)
        self.notify_enabled = False if notify_enabled is None else notify_enabled
        self.history = []

    def set_history(self, history):
        """Set the history list."""
        self.history = history

    def start(self, poll_interval=2):
        """Start the Telegram bot."""
        self.updater = Updater(API_TOKEN, use_context=True)
        dispatcher = self.updater.dispatcher
        
        # Register handlers
        dispatcher.add_handler(CommandHandler("start", self._start_command))
        dispatcher.add_handler(MessageHandler(Filters.photo, self._photo_handler))
        
        # Start polling
        self.updater.start_polling(poll_interval=poll_interval)
        return self.updater

    def stop(self):
        """Stop the Telegram bot."""
        if self.updater:
            self.updater.stop()

    def change_interval(self, interval):
        """Change the polling interval."""
        if self.updater:
            self.updater.stop()
            self.updater.start_polling(poll_interval=interval)

    def _start_command(self, update, context):
        """Handle /start command."""
        if update.message.from_user.id != AUTHORIZED_USER_ID:
            context.bot.send_message(
                chat_id=update.message.chat_id, 
                text="Sorry, you are not authorized to use this bot."
            )
            return
        
        context.bot.send_message(
            chat_id=update.message.chat_id, 
            text="Welcome to Screenshot Manager Bot! Send me screenshots from your phone, and I'll copy them to your PC clipboard."
        )

    def _photo_handler(self, update, context):
        """Handle incoming photos from Telegram."""
        global recent_hashes
        
        if update.message.from_user.id != AUTHORIZED_USER_ID:
            return
            
        try:
            photo = update.message.photo[-1]  # Highest quality photo
            file = context.bot.get_file(photo.file_id)
            timestamp = generate_timestamp()
            file_path = get_screenshot_path(timestamp)
            file.download(file_path)

            # De-duplication
            file_hash = calculate_hash(file_path)
            if file_hash in recent_hashes:
                import os
                os.remove(file_path)
                return
                
            recent_hashes.append(file_hash)
            if len(recent_hashes) > MAX_RECENT_HASHES:
                recent_hashes.pop(0)

            # Copy to clipboard
            copy_to_clipboard(file_path)

            # Update history
            self.history.append({"timestamp": timestamp, "path": file_path})
            save_history(self.history)

            # Update UI if callback is provided
            if self.update_ui_callback:
                self.update_ui_callback(f"Last screenshot: {timestamp}")

            # Send notification only if explicitly enabled
            if self.notify_enabled:
                try:
                    notification.notify(
                        title="Screenshot Manager",
                        message="Screenshot copied",  # Shorter message
                        timeout=1  # Very short timeout (1 second)
                    )
                except Exception as e:
                    print(f"Notification error: {str(e)}")

            context.bot.send_message(chat_id=update.message.chat_id, text="Image copied to clipboard.")
        except Exception as e:
            context.bot.send_message(chat_id=update.message.chat_id, text=f"Error: {str(e)}")
            if self.update_ui_callback:
                self.update_ui_callback(f"Error: {str(e)}") 