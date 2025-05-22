import os
import json
import customtkinter as ctk
from PIL import Image
import webbrowser
import threading
import time

from modules.cloud_service import CloudService

class SetupWizard:
    """Setup wizard for the Screenshot Manager"""
    
    def __init__(self, parent=None, on_complete=None):
        """
        Initialize the setup wizard
        
        Args:
            parent: Parent window or None
            on_complete: Callback function to call when setup is complete
        """
        self.parent = parent
        self.on_complete = on_complete
        self.wizard = None
        self.connection_test_in_progress = False
        self.telegram_id = ""
        self.service_url = "https://devshare-production.up.railway.app"  # Updated to Railway URL
        self.config_file = './config.json'
        
        # Load existing config if available
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    if 'telegram_id' in config:
                        self.telegram_id = config['telegram_id']
                    if 'service_url' in config:
                        self.service_url = config['service_url']
            except Exception as e:
                print(f"Error loading config: {e}")
    
    def _save_config(self):
        """Save configuration to file"""
        try:
            # Load existing config if file exists
            config = {}
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
            
            # Update with our values
            config['telegram_id'] = self.telegram_id
            config['service_url'] = self.service_url
            
            # Save back to file
            with open(self.config_file, 'w') as f:
                json.dump(config, f)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def show(self):
        """Show the setup wizard"""
        # Create wizard window
        self.wizard = ctk.CTkToplevel(self.parent) if self.parent else ctk.CTk()
        self.wizard.title("Screenshot Manager Setup")
        self.wizard.geometry("600x500")
        self.wizard.resizable(False, False)
        
        if self.parent:
            self.wizard.transient(self.parent)  # Set as transient to parent
            self.wizard.grab_set()  # Make it modal
            
            # Center on parent
            self.wizard.update_idletasks()
            x = self.parent.winfo_rootx() + (self.parent.winfo_width() - self.wizard.winfo_width()) // 2
            y = self.parent.winfo_rooty() + (self.parent.winfo_height() - self.wizard.winfo_height()) // 2
            self.wizard.geometry(f"+{x}+{y}")
        else:
            # Center on screen if no parent
            self.wizard.update_idletasks()
            width = self.wizard.winfo_width()
            height = self.wizard.winfo_height()
            x = (self.wizard.winfo_screenwidth() // 2) - (width // 2)
            y = (self.wizard.winfo_screenheight() // 2) - (height // 2)
            self.wizard.geometry(f"+{x}+{y}")
        
        # Main container with padding
        container = ctk.CTkFrame(self.wizard, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # App logo
        logo_path = os.path.join("public", "logo-big.png")
        if os.path.exists(logo_path):
            try:
                logo_image = Image.open(logo_path)
                logo_image = logo_image.resize((100, 100))
                logo_photo = ctk.CTkImage(light_image=logo_image, dark_image=logo_image, size=(100, 100))
                logo_label = ctk.CTkLabel(container, image=logo_photo, text="")
                logo_label._image = logo_photo  # Keep reference
                logo_label.pack(pady=(0, 10))
            except Exception as e:
                print(f"Error loading logo: {e}")
        
        # Title
        title_label = ctk.CTkLabel(
            container,
            text="Setup Wizard",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#1E88E5"
        )
        title_label.pack(pady=(0, 20))
        
        # Instructions
        instructions = (
            "Welcome to Screenshot Manager! This wizard will help you set up "
            "the application to work with the Telegram bot service."
        )
        
        instructions_label = ctk.CTkLabel(
            container,
            text=instructions,
            font=ctk.CTkFont(size=14),
            wraplength=550
        )
        instructions_label.pack(pady=(0, 20), fill="x")
        
        # Telegram ID Frame
        id_frame = ctk.CTkFrame(container, fg_color="#F5F7F9", corner_radius=10)
        id_frame.pack(fill="x", pady=(0, 15))
        
        id_title = ctk.CTkLabel(
            id_frame,
            text="Step 1: Enter Your Telegram ID",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#333333"
        )
        id_title.pack(anchor="w", padx=15, pady=(10, 5))
        
        # Telegram ID instructions
        id_instructions = (
            "To find your Telegram ID:\n"
            "1. Open Telegram and search for @userinfobot\n"
            "2. Start a chat with this bot\n"
            "3. The bot will reply with your User ID (a number)"
        )
        
        id_label = ctk.CTkLabel(
            id_frame,
            text=id_instructions,
            font=ctk.CTkFont(size=14),
            justify="left"
        )
        id_label.pack(anchor="w", padx=15, pady=(0, 10))
        
        # Telegram ID input
        id_input_frame = ctk.CTkFrame(id_frame, fg_color="transparent")
        id_input_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        id_label = ctk.CTkLabel(
            id_input_frame,
            text="Your Telegram ID:",
            font=ctk.CTkFont(size=14),
            width=120
        )
        id_label.pack(side="left")
        
        id_entry = ctk.CTkEntry(
            id_input_frame,
            width=320,
            height=30,
            placeholder_text="Enter your Telegram ID (e.g., 123456789)"
        )
        id_entry.pack(side="left", padx=10)
        if self.telegram_id:
            id_entry.insert(0, self.telegram_id)
            
        # Find ID button - opens Telegram
        find_id_button = ctk.CTkButton(
            id_frame,
            text="Open Telegram to Find Your ID",
            command=lambda: webbrowser.open("https://t.me/userinfobot"),
            height=30,
            width=200,
            fg_color="#0088cc",  # Telegram blue
            hover_color="#0077b5"
        )
        find_id_button.pack(pady=(0, 10))
        
        # Service URL Frame
        service_frame = ctk.CTkFrame(container, fg_color="#F5F7F9", corner_radius=10)
        service_frame.pack(fill="x", pady=(0, 15))
        
        service_title = ctk.CTkLabel(
            service_frame,
            text="Step 2: Service Connection",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#333333"
        )
        service_title.pack(anchor="w", padx=15, pady=(10, 5))
        
        # Service instructions
        service_instructions = (
            "Connect to the Screenshot Manager service to receive screenshots from "
            "the Telegram bot. The default URL should work unless instructed otherwise."
        )
        
        service_label = ctk.CTkLabel(
            service_frame,
            text=service_instructions,
            font=ctk.CTkFont(size=14),
            justify="left",
            wraplength=550
        )
        service_label.pack(anchor="w", padx=15, pady=(0, 10))
        
        # Service URL input
        url_input_frame = ctk.CTkFrame(service_frame, fg_color="transparent")
        url_input_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        url_label = ctk.CTkLabel(
            url_input_frame,
            text="Service URL:",
            font=ctk.CTkFont(size=14),
            width=120
        )
        url_label.pack(side="left")
        
        url_entry = ctk.CTkEntry(
            url_input_frame,
            width=320,
            height=30
        )
        url_entry.insert(0, self.service_url)
        url_entry.pack(side="left", padx=10)
        
        # Status message
        status_var = ctk.StringVar(value="")
        status_label = ctk.CTkLabel(
            container,
            textvariable=status_var,
            font=ctk.CTkFont(size=14),
            text_color="#555555"
        )
        status_label.pack(pady=10)
        
        # Test connection button
        test_button = ctk.CTkButton(
            container,
            text="Test Connection",
            command=lambda: self._test_connection(id_entry.get(), url_entry.get(), status_var, test_button),
            height=35,
            width=150
        )
        test_button.pack(pady=(0, 10))
        
        # Save button
        def save_settings():
            user_id = id_entry.get().strip()
            url = url_entry.get().strip()
            
            if not user_id:
                status_var.set("Please enter your Telegram ID")
                return
            
            self.telegram_id = user_id
            self.service_url = url
            self._save_config()
            
            # Close the wizard
            self.wizard.destroy()
            
            # Call the completion callback
            if self.on_complete:
                self.on_complete(user_id, url)
        
        save_button = ctk.CTkButton(
            container,
            text="Save and Continue",
            command=save_settings,
            height=35,
            width=150,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#1976D2",
            hover_color="#1565C0"
        )
        save_button.pack(pady=10)
        
        # If not called from another window, run mainloop
        if not self.parent:
            self.wizard.mainloop()
    
    def _test_connection(self, user_id, service_url, status_var, test_button):
        """Test the connection to the service"""
        # Validate inputs
        user_id = user_id.strip()
        service_url = service_url.strip()
        
        if not user_id:
            status_var.set("Please enter your Telegram ID")
            return
        
        if not service_url:
            status_var.set("Please enter the service URL")
            return
        
        if self.connection_test_in_progress:
            return
            
        # Disable button during test
        test_button.configure(state="disabled", text="Testing...")
        self.connection_test_in_progress = True
        
        # Function to run in thread
        def run_test():
            try:
                status_var.set("Connecting to service...")
                
                # Create a temporary CloudService instance
                service = CloudService(user_id, config_file=None)
                service.service_url = service_url
                
                # Try to connect
                result = service.connect()
                
                if result:
                    status_var.set("Connection successful! You can now use the app.")
                else:
                    status_var.set("Connection failed. Please check your settings.")
                
                # Clean up
                service.disconnect()
                
            except Exception as e:
                status_var.set(f"Error: {str(e)}")
            finally:
                # Re-enable button
                test_button.configure(state="normal", text="Test Connection")
                self.connection_test_in_progress = False
        
        # Start test in a separate thread
        threading.Thread(target=run_test).start() 