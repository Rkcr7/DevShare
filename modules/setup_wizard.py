import os
import json
import customtkinter as ctk
from PIL import Image
import webbrowser
import threading
import time

from modules.cloud_service import CloudService

class SetupWizard:
    """Setup wizard for the DevShare application"""
    
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
                
            print(f"Configuration saved to {self.config_file}")
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def show(self):
        """Show the setup wizard"""
        # Create wizard window
        self.wizard = ctk.CTkToplevel(self.parent) if self.parent else ctk.CTk()
        self.wizard.title("Devshare Setup Wizard")
        self.wizard.geometry("500x500")  # More compact size
        self.wizard.resizable(False, False)  # Fixed size for better layout
        
        if self.parent:
            self.wizard.transient(self.parent)
            self.wizard.grab_set()
            
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
        
        # Main container
        container = ctk.CTkFrame(self.wizard)
        container.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Header frame
        header_frame = ctk.CTkFrame(container, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 10))
        
        # App logo
        logo_path = os.path.join("public", "logo-big.png")
        if os.path.exists(logo_path):
            try:
                logo_image = Image.open(logo_path)
                logo_image = logo_image.resize((60, 60))  # Smaller logo
                logo_photo = ctk.CTkImage(light_image=logo_image, dark_image=logo_image, size=(60, 60))
                logo_label = ctk.CTkLabel(header_frame, image=logo_photo, text="")
                logo_label._image = logo_photo  # Keep reference
                logo_label.pack(side="left", padx=(0, 10))
            except Exception as e:
                print(f"Error loading logo: {e}")
        
        # Title
        title_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_frame.pack(side="left", fill="both", expand=True)
        
        title_label = ctk.CTkLabel(
            title_frame,
            text="Devshare Setup Wizard",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#1E88E5"
        )
        title_label.pack(anchor="w")
        
        subtitle_label = ctk.CTkLabel(
            title_frame,
            text="Connect your Telegram ID to receive screenshots",
            font=ctk.CTkFont(size=12),
            text_color="#555555"
        )
        subtitle_label.pack(anchor="w")
        
        # Status message
        status_var = ctk.StringVar(value="")
        status_label = ctk.CTkLabel(
            container,
            textvariable=status_var,
            font=ctk.CTkFont(size=13),
            text_color="#555555",
            wraplength=470
        )
        status_label.pack(pady=(0, 10), fill="x")
        
        # Content frame
        content_frame = ctk.CTkFrame(container)
        content_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Telegram ID Frame
        id_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        id_frame.pack(fill="x", padx=10, pady=10)
        
        id_title = ctk.CTkLabel(
            id_frame,
            text="Step 1: Enter Your Telegram ID",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        id_title.pack(fill="x", pady=(0, 5))
        
        # Compact instructions
        id_instructions = ctk.CTkLabel(
            id_frame,
            text="To find your ID: Open Telegram → @userinfobot → Start chat → Get ID",
            font=ctk.CTkFont(size=12),
            justify="left",
            anchor="w"
        )
        id_instructions.pack(fill="x", pady=(0, 10))
        
        # ID input row
        id_input_frame = ctk.CTkFrame(id_frame, fg_color="transparent")
        id_input_frame.pack(fill="x")
        
        id_label = ctk.CTkLabel(
            id_input_frame,
            text="Your Telegram ID:",
            font=ctk.CTkFont(size=13),
            width=110
        )
        id_label.pack(side="left")
        
        id_entry = ctk.CTkEntry(
            id_input_frame,
            height=30,
            placeholder_text="Enter ID (e.g., 123456789)"
        )
        id_entry.pack(side="left", fill="x", expand=True, padx=(5, 0))
        
        if self.telegram_id:
            id_entry.insert(0, self.telegram_id)
        
        # Button row
        id_buttons_frame = ctk.CTkFrame(id_frame, fg_color="transparent")
        id_buttons_frame.pack(fill="x", pady=(10, 0))
        
        find_id_button = ctk.CTkButton(
            id_buttons_frame,
            text="Open Telegram",
            command=lambda: webbrowser.open("https://t.me/userinfobot"),
            height=30,
            fg_color="#0088cc",
            hover_color="#0077b5",
            width=120
        )
        find_id_button.pack(side="left")
        
        submit_id_button = ctk.CTkButton(
            id_buttons_frame,
            text="Submit ID",
            command=lambda: self._submit_telegram_id(id_entry.get(), status_var),
            height=30,
            fg_color="#4CAF50",
            hover_color="#45a049",
            width=120
        )
        submit_id_button.pack(side="right")
        
        # Service URL Frame
        service_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        service_frame.pack(fill="x", padx=10, pady=10)
        
        service_title = ctk.CTkLabel(
            service_frame,
            text="Step 2: Service Connection",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        service_title.pack(fill="x", pady=(0, 5))
        
        # Compact instructions
        service_instructions = ctk.CTkLabel(
            service_frame,
            text="Connect to Devshare to receive screenshots from Telegram",
            font=ctk.CTkFont(size=12),
            justify="left",
            anchor="w"
        )
        service_instructions.pack(fill="x", pady=(0, 10))
        
        # URL input row
        url_input_frame = ctk.CTkFrame(service_frame, fg_color="transparent")
        url_input_frame.pack(fill="x")
        
        url_label = ctk.CTkLabel(
            url_input_frame,
            text="Service URL:",
            font=ctk.CTkFont(size=13),
            width=110
        )
        url_label.pack(side="left")
        
        url_entry = ctk.CTkEntry(
            url_input_frame,
            height=30
        )
        url_entry.insert(0, self.service_url)
        url_entry.pack(side="left", fill="x", expand=True, padx=(5, 0))
        
        # Bottom buttons
        buttons_frame = ctk.CTkFrame(container, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=(10, 0))
        
        def save_settings():
            user_id = id_entry.get().strip()
            url = url_entry.get().strip()
            
            if not user_id:
                status_var.set("Please enter your Telegram ID")
                return
            
            self.telegram_id = user_id
            self.service_url = url
            
            # Create config.json
            if self._save_config():
                status_var.set("Configuration saved successfully! Created config.json file.")
                self.wizard.update()
                
                # Close the wizard with a delay to avoid animation errors
                def close_window():
                    if self.wizard:
                        try:
                            self.wizard.destroy()
                            
                            # Call the completion callback
                            if self.on_complete:
                                self.on_complete(user_id, url)
                        except Exception as e:
                            print(f"Error closing wizard: {e}")
                
                # Schedule the window close after animations complete
                self.wizard.after(300, close_window)
                
            else:
                status_var.set("Error saving configuration. Please try again.")
        
        save_button = ctk.CTkButton(
            buttons_frame,
            text="Save and Continue",
            command=save_settings,
            height=35,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#1976D2",
            hover_color="#1565C0",
            width=150
        )
        save_button.pack(side="right")
        
        # Run mainloop if not called from another window
        if not self.parent:
            self.wizard.mainloop()
    
    def _submit_telegram_id(self, user_id, status_var):
        """Handle the submit ID button click"""
        user_id = user_id.strip()
        
        if not user_id:
            status_var.set("Please enter your Telegram ID")
            return
        
        # Store the ID and update status
        self.telegram_id = user_id
        
        # Create a temporary config file to ensure the ID is stored
        temp_save = self._save_config()
        if temp_save:
            status_var.set(f"Telegram ID {user_id} stored successfully! Click 'Save and Continue' to complete setup.")
        else:
            status_var.set(f"Telegram ID {user_id} stored temporarily. There was an issue saving to config.json.") 