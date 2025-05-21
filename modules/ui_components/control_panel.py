import customtkinter as ctk
import os
from PIL import Image
import tkinter as tk

class ControlPanel:
    """Component that handles the control buttons and settings"""
    
    def __init__(self, parent, bot=None, update_status_callback=None, delete_all_callback=None, refresh_callback=None):
        self.parent = parent
        self.bot = bot
        self.update_status_callback = update_status_callback
        self.delete_all_callback = delete_all_callback
        self.refresh_callback = refresh_callback
        
        self.interval_entry = None
        self.notify_enabled = None
        
        self._create_ui()
        
    def _create_ui(self):
        """Create the control panel UI components"""
        # Control buttons in a compact panel
        controls_panel = ctk.CTkFrame(self.parent, corner_radius=10, fg_color="#F5F7F9", border_width=1, border_color="#E0E6ED")
        controls_panel.pack(fill="x", pady=(0, 10))
        
        # Section title for controls
        controls_title = ctk.CTkLabel(
            controls_panel, 
            text="Controls",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#333333"
        )
        controls_title.pack(anchor="w", padx=15, pady=(10, 5))
        
        # Control buttons with improved styling in a more compact layout
        control_frame = ctk.CTkFrame(controls_panel, fg_color="transparent")
        control_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        # Create a horizontal layout for all buttons
        button_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=5)
        
        # Delete all button
        delete_all_button = ctk.CTkButton(
            button_frame, 
            text="Delete All",
            command=self.delete_all_screenshots,
            height=32,
            width=100,
            fg_color="#D32F2F",
            hover_color="#B71C1C",
            corner_radius=8,
            font=ctk.CTkFont(size=13)
        )
        delete_all_button.pack(side="left", padx=(0, 10))
        
        # Refresh button
        refresh_button = ctk.CTkButton(
            button_frame, 
            text="Refresh",
            command=self.refresh,
            height=32,
            width=100,
            corner_radius=8,
            font=ctk.CTkFont(size=13),
            hover_color="#0078D4"
        )
        refresh_button.pack(side="left", padx=(0, 10))
        
        # About button
        about_button = ctk.CTkButton(
            button_frame, 
            text="About",
            command=self.show_about,
            height=32,
            width=100,
            corner_radius=8,
            font=ctk.CTkFont(size=13),
            fg_color="#2E7D32",
            hover_color="#1B5E20"
        )
        about_button.pack(side="left")
        
        # Initialize notify_enabled and create a checkbox
        self.notify_enabled = ctk.BooleanVar(value=False)
        notify_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        notify_frame.pack(fill="x", pady=5)
        
        notify_check = ctk.CTkCheckBox(
            notify_frame, 
            text="Notifications", 
            variable=self.notify_enabled, 
            command=self.update_notify_setting,
            height=28,
            checkbox_height=20,
            checkbox_width=20,
            corner_radius=5,
            border_width=2,
            font=ctk.CTkFont(size=13),
            text_color="#333333"
        )
        notify_check.pack(side="left")
        
    def show_about(self):
        """Show About dialog with app logo and information."""
        about_window = ctk.CTkToplevel(self.parent)
        about_window.title("About Screenshot Manager")
        about_window.geometry("400x350")
        about_window.resizable(False, False)
        about_window.focus_set()  # Set focus to the window
        about_window.grab_set()   # Make the window modal
        
        # Make the window appear in center of parent
        about_window.update_idletasks()
        x = self.parent.winfo_rootx() + (self.parent.winfo_width() - about_window.winfo_width()) // 2
        y = self.parent.winfo_rooty() + (self.parent.winfo_height() - about_window.winfo_height()) // 2
        about_window.geometry(f"+{x}+{y}")
        
        # Container frame
        container = ctk.CTkFrame(about_window, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Load and display the big logo
        logo_path = os.path.join("public", "logo-big.png")
        if os.path.exists(logo_path):
            try:
                logo_image = Image.open(logo_path)
                logo_image = logo_image.resize((128, 128))  # Resize for dialog
                logo_photo = ctk.CTkImage(light_image=logo_image, dark_image=logo_image, size=(128, 128))
                logo_label = ctk.CTkLabel(container, image=logo_photo, text="")
                logo_label._image = logo_photo  # Keep reference
                logo_label.pack(pady=(0, 10))
            except Exception as e:
                print(f"Error loading logo: {e}")
        
        # App title
        title_label = ctk.CTkLabel(
            container,
            text="Screenshot Manager",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#1E88E5"
        )
        title_label.pack(pady=5)
        
        # App version
        version_label = ctk.CTkLabel(
            container,
            text="Version 1.0",
            font=ctk.CTkFont(size=14),
            text_color="#555555"
        )
        version_label.pack(pady=5)
        
        # App description
        desc_label = ctk.CTkLabel(
            container,
            text="Easily manage screenshots sent from your phone\nvia Telegram to your PC.",
            font=ctk.CTkFont(size=14),
            text_color="#333333"
        )
        desc_label.pack(pady=10)
        
        # Close button
        close_button = ctk.CTkButton(
            container,
            text="Close",
            command=about_window.destroy,
            height=32,
            width=100,
            corner_radius=8,
            font=ctk.CTkFont(size=13)
        )
        close_button.pack(pady=10)
        
    def update_notify_setting(self):
        """Update the bot's notification setting when checkbox is toggled."""
        if self.bot and hasattr(self, 'notify_enabled'):
            self.bot.notify_enabled = self.notify_enabled.get()
            if self.update_status_callback:
                status = "enabled" if self.notify_enabled.get() else "disabled"
                self.update_status_callback(f"Notifications {status}")
        
    def delete_all_screenshots(self):
        """Delete all screenshots."""
        if self.delete_all_callback:
            self.delete_all_callback()
            
    def change_interval(self, value):
        """Change the polling interval."""
        if not self.bot:
            if self.update_status_callback:
                self.update_status_callback("Bot not initialized")
            return
            
        try:
            interval = float(value)
            if interval <= 0:
                raise ValueError("Interval must be positive.")
                
            self.bot.change_interval(interval)
            if self.update_status_callback:
                self.update_status_callback(f"Polling interval set to {interval} seconds")
        except ValueError as e:
            if self.update_status_callback:
                self.update_status_callback(f"Error: {str(e)}")
    
    def toggle_theme(self):
        """Toggle between light and dark themes."""
        current_mode = ctk.get_appearance_mode()
        new_mode = "dark" if current_mode == "light" else "light"
        ctk.set_appearance_mode(new_mode)
        if self.update_status_callback:
            self.update_status_callback(f"Theme switched to {new_mode}")
            
    def refresh(self):
        """Refresh the UI."""
        if self.refresh_callback:
            self.refresh_callback() 