import tkinter as tk
import customtkinter as ctk
import sys
import os
import time
from PIL import Image

from modules.utils import load_history, save_history
from modules.ui_components.screenshot_list import ScreenshotList
from modules.ui_components.control_panel import ControlPanel
from modules.ui_components.search_panel import SearchPanel

class ScreenshotUI:
    """Main UI class that coordinates all UI components"""
    
    def __init__(self, bot=None):
        self.bot = bot
        self.history = []
        self.root = None
        self.status_label = None
        
        # Component references
        self.screenshot_list = None
        self.control_panel = None
        self.search_panel = None
        
        # Refresh control
        self.last_refresh_time = 0
        self.refresh_cooldown = 2.0  # Minimum seconds between refreshes
        self.auto_refresh_interval = 10000  # Increased from 5000ms to 10000ms (10 seconds)
        
        # Load history
        self.load_history()
        
        # Initialize UI
        self._setup_ui()
        
        # If bot is provided, set the update UI callback
        if self.bot:
            self.bot.update_ui_callback = self.update_status
        
    def load_history(self):
        """Load history from file."""
        self.history = load_history()
        if self.bot:
            self.bot.set_history(self.history)
            
    def _setup_ui(self):
        """Set up the main UI components."""
        # Set up UI theme - permanently light mode
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Create the main window
        self.root = ctk.CTk()
        self.root.title("Screenshot Manager")
        self.root.geometry("750x600")  # Smaller window size
        self.root.minsize(700, 500)
        
        # Set app background color
        self.root.configure(fg_color="#F0F4F8")
        
        # Set icon - use the favicon from public folder
        favicon_path = os.path.join("public", "favicon.ico")
        if os.path.exists(favicon_path):
            self.root.iconbitmap(favicon_path)
        
        # Set up window close protocol to exit the application
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Main outer padding container
        outer_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        outer_frame.pack(fill="both", expand=True, padx=15, pady=15)  # Reduced padding
        
        # Header with app title and status
        header_frame = ctk.CTkFrame(
            outer_frame, 
            fg_color="#FFFFFF",
            corner_radius=10,
            border_width=1,
            border_color="#E0E6ED",
            height=60  # Reduced height
        )
        header_frame.pack(fill="x", pady=(0, 10))  # Reduced padding
        header_frame.pack_propagate(False)  # Don't shrink to fit contents
        
        # App logo - use the small logo from public folder
        logo_path = os.path.join("public", "logo-small.png")
        if os.path.exists(logo_path):
            try:
                # Load and display the logo
                logo_image = Image.open(logo_path)
                logo_image = logo_image.resize((24, 24))  # Resize to fit in header
                logo_photo = ctk.CTkImage(light_image=logo_image, dark_image=logo_image, size=(24, 24))
                logo_label = ctk.CTkLabel(header_frame, image=logo_photo, text="")
                logo_label._image = logo_photo  # Keep a reference to prevent garbage collection
                logo_label.pack(side="left", padx=(12, 8), pady=18)
            except Exception as e:
                print(f"Error loading logo: {e}")
                # Fallback to placeholder if logo can't be loaded
                logo_frame = ctk.CTkFrame(header_frame, fg_color="#1E88E5", width=24, height=24, corner_radius=6)
                logo_frame.pack(side="left", padx=(12, 8), pady=18)
        else:
            # Fallback to placeholder if logo file doesn't exist
            logo_frame = ctk.CTkFrame(header_frame, fg_color="#1E88E5", width=24, height=24, corner_radius=6)
            logo_frame.pack(side="left", padx=(12, 8), pady=18)
        
        # App title with better font but slightly smaller
        title_label = ctk.CTkLabel(
            header_frame,
            text="Screenshot Manager",
            font=ctk.CTkFont(size=18, weight="bold"),  # Reduced font size
            text_color="#1E88E5"
        )
        title_label.pack(side="left", pady=18)  # Adjusted padding
        
        # Status label with modern styling
        self.status_label = ctk.CTkLabel(
            header_frame,
            text="Status: Ready",
            font=ctk.CTkFont(size=12),  # Reduced font size
            text_color="#555555"
        )
        self.status_label.pack(side="right", padx=12, pady=18)  # Adjusted padding
        
        # Top row frame (for search and interval)
        top_row = ctk.CTkFrame(outer_frame, fg_color="transparent")
        top_row.pack(fill="x", pady=(0, 10))
        
        # Left section for search panel
        search_frame = ctk.CTkFrame(top_row, fg_color="transparent")
        search_frame.pack(side="left", fill="x", expand=True)
        
        # Create search panel in left section
        self.search_panel = SearchPanel(
            search_frame, 
            search_callback=self.filter_history
        )
        
        # Right section for interval settings
        interval_frame = ctk.CTkFrame(top_row, corner_radius=10, fg_color="#F5F7F9", border_width=1, border_color="#E0E6ED")
        interval_frame.pack(side="right", padx=(10, 0))
        
        # Create interval controls with more compact layout
        interval_inner = ctk.CTkFrame(interval_frame, fg_color="transparent")
        interval_inner.pack(padx=12, pady=12)
        
        interval_label = ctk.CTkLabel(
            interval_inner,
            text="Polling (sec):",
            font=ctk.CTkFont(size=12),
            text_color="#444444"
        )
        interval_label.pack(side="left")
        
        interval_entry = ctk.CTkEntry(
            interval_inner,
            width=50,
            height=28,
            corner_radius=6,
            font=ctk.CTkFont(size=12),
            border_width=1,
            border_color="#DDDDDD",
            fg_color="#FFFFFF"
        )
        interval_entry.insert(0, "2")
        interval_entry.pack(side="left", padx=8)
        
        set_button = ctk.CTkButton(
            interval_inner,
            text="Set",
            font=ctk.CTkFont(size=12),
            width=50,
            height=28,
            corner_radius=6,
            hover_color="#0078D4",
            command=lambda: self.control_panel.change_interval(interval_entry.get()) if self.control_panel else None
        )
        set_button.pack(side="left")
        
        # Create the screenshot list component (improved styling is in the component)
        self.screenshot_list = ScreenshotList(
            outer_frame,
            bot=self.bot, 
            update_status_callback=self.update_status
        )
        
        # Initialize the control panel (improved styling is in the component)
        self.control_panel = ControlPanel(
            outer_frame,
            bot=self.bot, 
            update_status_callback=self.update_status,
            delete_all_callback=self.delete_all_screenshots,
            refresh_callback=self.refresh_history
        )

        # Populate initial history
        self.update_history_list()
        
        # Set up auto-refresh
        self.root.after(self.auto_refresh_interval, self.auto_refresh)
        
    def on_close(self):
        """Handle window closing event."""
        print("Shutting down application...")
        # Stop the bot if it exists
        if self.bot:
            self.bot.stop()
        # Destroy the root window
        if self.root:
            self.root.destroy()
        # Exit the application
        sys.exit(0)
        
    def run(self):
        """Run the UI main loop."""
        self.root.mainloop()
        
    def stop(self):
        """Stop the UI."""
        if self.root:
            self.root.destroy()
            
    def update_status(self, message):
        """Update the status label."""
        try:
            self.status_label.configure(text=f"Status: {message}")
        except:
            pass  # Handle case where UI is not fully initialized
            
    def update_history_list(self, query=""):
        """Update the history list, optionally filtered by query."""
        if self.screenshot_list:
            self.screenshot_list.update_list(self.history, query)
            
    def filter_history(self, query=""):
        """Filter history based on search query."""
        self.update_history_list(query)
        
    def refresh_history(self, force=False):
        """Manually refresh the history display with cooldown protection."""
        current_time = time.time()
        
        # Only refresh if forced or if cooldown period has passed
        if force or (current_time - self.last_refresh_time) >= self.refresh_cooldown:
            self.last_refresh_time = current_time
            self.load_history()
            query = self.search_panel.get_query() if self.search_panel else ""
            self.update_history_list(query)
            self.update_status("History refreshed")
        
    def delete_all_screenshots(self):
        """Delete all screenshots."""
        if self.screenshot_list:
            self.screenshot_list.delete_all_screenshots()
            # Update our local history after deletion
            self.history = self.screenshot_list.history
        
    def auto_refresh(self):
        """Periodically refresh the history list with cooldown protection."""
        # Only refresh if no recent manual refresh
        current_time = time.time()
        if (current_time - self.last_refresh_time) >= self.refresh_cooldown:
            query = self.search_panel.get_query() if self.search_panel else ""
            self.load_history()  # Reload from file
            self.update_history_list(query)
            self.last_refresh_time = current_time
            
        # Schedule next auto refresh
        self.root.after(self.auto_refresh_interval, self.auto_refresh) 