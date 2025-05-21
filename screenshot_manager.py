import os
import json
import hashlib
import platform
import subprocess
from datetime import datetime
import tkinter as tk
from tkinter import ttk
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
from PIL import Image
import io
import customtkinter as ctk
from customtkinter import CTkImage
from plyer import notification

# Configuration
API_TOKEN = '7594536865:AAEX7CXhlQPy5v34fJqST-iTQh1x73xMN2U'  # Your bot's API token
AUTHORIZED_USER_ID = 860118391  # Your Telegram user ID
SCREENSHOT_DIR = './screenshots'
HISTORY_FILE = './screenshots.json'
RECENT_HASHES = 5  # Number of recent hashes for de-duplication
THUMBNAIL_SIZE = (50, 50)  # Thumbnail dimensions

# Ensure directories and files exist
os.makedirs(SCREENSHOT_DIR, exist_ok=True)
if not os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, 'w') as f:
        json.dump([], f)

# Load history
with open(HISTORY_FILE, 'r') as f:
    history = json.load(f)

# Recent screenshot hashes for de-duplication
recent_hashes = []

# Global variables
updater = None
notify_enabled = None
root = None

def calculate_hash(file_path):
    """Calculate MD5 hash of a file."""
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        hasher.update(f.read())
    return hasher.hexdigest()

def copy_to_clipboard(image_path):
    """Copy an image to the clipboard based on the OS."""
    try:
        if platform.system() == 'Windows':
            import win32clipboard
            image = Image.open(image_path)
            output = io.BytesIO()
            image.convert("RGB").save(output, "BMP")
            data = output.getvalue()[14:]  # Skip BMP header
            output.close()
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
            win32clipboard.CloseClipboard()
        elif platform.system() == 'Darwin':  # macOS
            script = f'set the clipboard to (read (POSIX file "{image_path}") as picture)'
            subprocess.run(['osascript', '-e', script], check=True)
        elif platform.system() == 'Linux':
            subprocess.run(['xclip', '-selection', 'clipboard', '-t', 'image/png', '-i', image_path], check=True)
        return True
    except Exception as e:
        raise Exception(f"Clipboard error: {str(e)}")

def photo_handler(update, context):
    """Handle incoming photos from Telegram."""
    if update.message.from_user.id != AUTHORIZED_USER_ID:
        return
    try:
        photo = update.message.photo[-1]  # Highest quality photo
        file = context.bot.get_file(photo.file_id)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(SCREENSHOT_DIR, f"screenshot_{timestamp}.png")
        file.download(file_path)

        # De-duplication
        file_hash = calculate_hash(file_path)
        if file_hash in recent_hashes:
            os.remove(file_path)
            return
        recent_hashes.append(file_hash)
        if len(recent_hashes) > RECENT_HASHES:
            recent_hashes.pop(0)

        # Copy to clipboard
        copy_to_clipboard(file_path)

        # Update history
        history.append({"timestamp": timestamp, "path": file_path})
        with open(HISTORY_FILE, 'w') as f:
            json.dump(history, f)

        # Update UI
        update_history_list()
        update_status(f"Last screenshot: {timestamp}")

        # Send notification
        if notify_enabled.get():
            notification.notify(
                title="Screenshot Manager",
                message="New screenshot copied to clipboard.",
                timeout=5
            )

        context.bot.send_message(chat_id=update.message.chat_id, text="Image copied to clipboard.")
    except Exception as e:
        context.bot.send_message(chat_id=update.message.chat_id, text=f"Error: {str(e)}")
        update_status(f"Error: {str(e)}")

def start_command(update, context):
    """Handle /start command."""
    if update.message.from_user.id != AUTHORIZED_USER_ID:
        context.bot.send_message(chat_id=update.message.chat_id, 
                               text="Sorry, you are not authorized to use this bot.")
        return
    
    context.bot.send_message(chat_id=update.message.chat_id, 
                           text="Welcome to Screenshot Manager Bot! Send me screenshots from your phone, and I'll copy them to your PC clipboard.")

def update_history_list(query=""):
    """Update the history listbox, optionally filtered by query."""
    listbox.delete(*listbox.get_children())
    for i, item in enumerate(history):
        if query.lower() in item['timestamp'].lower() or query.lower() in item['path'].lower():
            try:
                # Generate thumbnail
                img = Image.open(item['path'])
                img.thumbnail(THUMBNAIL_SIZE)
                photo = CTkImage(light_image=img, dark_image=img, size=THUMBNAIL_SIZE)
                listbox.insert("", "end", image=photo, values=(item['timestamp'], item['path']))
                # Store photo to prevent garbage collection
                listbox.image_list.append(photo)
            except Exception:
                listbox.insert("", "end", values=(item['timestamp'], item['path']))

def recopy_screenshot(event):
    """Re-copy a selected screenshot to the clipboard."""
    selected = listbox.selection()
    if selected:
        index = [i for i, item in enumerate(history) if item['path'] == listbox.item(selected[0])['values'][1]][0]
        try:
            copy_to_clipboard(history[index]['path'])
            ctk.CTkMessageBox(
                title="Success",
                message="Screenshot copied to clipboard again.",
                icon="info"
            )
            update_status(f"Re-copied: {history[index]['timestamp']}")
        except Exception as e:
            ctk.CTkMessageBox(title="Error", message=str(e), icon="cancel")

def delete_screenshot():
    """Delete a selected screenshot from history and disk."""
    selected = listbox.selection()
    if selected:
        index = [i for i, item in enumerate(history) if item['path'] == listbox.item(selected[0])['values'][1]][0]
        try:
            os.remove(history[index]['path'])
            history.pop(index)
            with open(HISTORY_FILE, 'w') as f:
                json.dump(history, f)
            update_history_list()
            ctk.CTkMessageBox(title="Success", message="Screenshot deleted.", icon="info")
            update_status("Screenshot deleted")
        except Exception as e:
            ctk.CTkMessageBox(title="Error", message=str(e), icon="cancel")

def change_interval():
    """Update the polling interval."""
    global updater
    try:
        interval = float(interval_entry.get())
        if interval <= 0:
            raise ValueError("Interval must be positive.")
        updater.stop()
        updater.start_polling(poll_interval=interval)
        ctk.CTkMessageBox(title="Success", message=f"Polling interval set to {interval} seconds.", icon="info")
        update_status(f"Polling interval: {interval} seconds")
    except ValueError as e:
        ctk.CTkMessageBox(title="Error", message=str(e), icon="cancel")

def filter_history():
    """Filter history based on search query."""
    update_history_list(search_entry.get())

def toggle_theme():
    """Switch between light and dark themes."""
    ctk.set_appearance_mode("dark" if ctk.get_appearance_mode() == "Light" else "light")
    update_status("Theme switched")

def update_status(message):
    """Update the status label."""
    status_label.configure(text=f"Status: {message}")

def auto_refresh_history():
    """Periodically refresh the history list using Tkinter's after method."""
    update_history_list()
    # Schedule the next refresh using Tkinter's after method
    root.after(5000, auto_refresh_history)  # 5000 ms = 5 seconds

def main():
    global updater, status_label, interval_entry, listbox, search_entry, notify_enabled, root

    # Set up UI
    ctk.set_appearance_mode("light")  # Start with light theme
    ctk.set_default_color_theme("blue")  # Sleek blue theme
    root = ctk.CTk()
    root.title("Screenshot Manager")
    root.geometry("700x500")
    root.minsize(600, 400)
    
    # Initialize notify_enabled after creating the root window
    notify_enabled = ctk.BooleanVar(value=True)

    # Status label
    status_label = ctk.CTkLabel(root, text="Status: Bot is running...", font=ctk.CTkFont(size=14, weight="bold"))
    status_label.pack(pady=10)

    # Interval setting
    interval_frame = ctk.CTkFrame(root)
    interval_label = ctk.CTkLabel(interval_frame, text="Polling Interval (seconds):")
    interval_label.pack(side="left")
    interval_entry = ctk.CTkEntry(interval_frame, width=60)
    interval_entry.insert(0, "2")  # Default interval
    interval_entry.pack(side="left", padx=10)
    interval_button = ctk.CTkButton(interval_frame, text="Set", command=change_interval)
    interval_button.pack(side="left")
    interval_frame.pack(pady=10)

    # Search bar
    search_frame = ctk.CTkFrame(root)
    search_label = ctk.CTkLabel(search_frame, text="Search History:")
    search_label.pack(side="left")
    search_entry = ctk.CTkEntry(search_frame, width=300)
    search_entry.pack(side="left", padx=10)
    search_button = ctk.CTkButton(search_frame, text="Search", command=filter_history)
    search_button.pack(side="left")
    search_frame.pack(pady=10)

    # Screenshot history
    history_frame = ctk.CTkFrame(root)
    listbox = ttk.Treeview(history_frame, columns=("Timestamp", "Path"), show="tree headings", height=12)
    listbox.heading("Timestamp", text="Timestamp")
    listbox.heading("Path", text="File Path")
    listbox.column("Timestamp", width=150)
    listbox.column("Path", width=350)
    listbox.image_list = []  # Store images to prevent garbage collection
    scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=listbox.yview)
    listbox.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    listbox.pack(side="left", fill="both", expand=True)
    history_frame.pack(pady=10, fill="both", expand=True)
    listbox.bind('<Double-Button-1>', recopy_screenshot)

    # Control buttons
    control_frame = ctk.CTkFrame(root)
    delete_button = ctk.CTkButton(control_frame, text="Delete Selected", command=delete_screenshot)
    delete_button.pack(side="left", padx=5)
    recopy_button = ctk.CTkButton(control_frame, text="Re-copy Last", command=lambda: recopy_screenshot(None) if history else None)
    recopy_button.pack(side="left", padx=5)
    notify_check = ctk.CTkCheckBox(control_frame, text="Notifications", variable=notify_enabled)
    notify_check.pack(side="left", padx=5)
    theme_button = ctk.CTkButton(control_frame, text="Toggle Theme", command=toggle_theme)
    theme_button.pack(side="left", padx=5)
    control_frame.pack(pady=10)

    # Populate initial history
    update_history_list()

    # Set up bot
    updater = Updater(API_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start_command))
    dispatcher.add_handler(MessageHandler(Filters.photo, photo_handler))
    updater.start_polling(poll_interval=2)

    # Start auto-refresh using Tkinter's after method
    root.after(5000, auto_refresh_history)  # 5000 ms = 5 seconds

    # Run UI
    root.mainloop()

    # Cleanup on exit
    updater.stop()

if __name__ == "__main__":
    main() 