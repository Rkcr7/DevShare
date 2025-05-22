import os
import json
import requests
import base64
from io import BytesIO
import threading
import time
from PIL import Image
from datetime import datetime
import logging
import random

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CloudService:
    """Client for interacting with the DevShare cloud service"""
    
    def __init__(self, telegram_id, callback=None, config_file='./config.json'):
        """
        Initialize the cloud service client
        
        Args:
            telegram_id (str): The user's Telegram ID
            callback (callable): Function to call when new screenshots are received
            config_file (str): Path to the configuration file
        """
        self.telegram_id = telegram_id
        self.callback = callback
        self.config_file = config_file
        self.connection_id = None
        self.service_url = "https://devshare-production.up.railway.app"  # Updated to Railway URL
        self.polling_interval = 5  # Seconds between polling for new screenshots
        self.connected = False
        self.stop_event = threading.Event()
        self.polling_thread = None
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 10
        self.reconnect_backoff_base = 2  # For exponential backoff
        self.reconnect_max_delay = 60  # Maximum delay between reconnection attempts
        self.reconnect_jitter = 0.5  # Random jitter factor to avoid thundering herd
        
        # Load config if it exists
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file"""
        try:
            if self.config_file and os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    if 'service_url' in config:
                        self.service_url = config['service_url']
                    if 'connection_id' in config:
                        self.connection_id = config['connection_id']
        except Exception as e:
            logger.error(f"Error loading config: {str(e)}")
    
    def _save_config(self):
        """Save configuration to file"""
        try:
            if not self.config_file:
                return
                
            # Load existing config if file exists
            config = {}
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
            
            # Update with our values
            config['service_url'] = self.service_url
            if self.connection_id:
                config['connection_id'] = self.connection_id
            
            # Save back to file
            with open(self.config_file, 'w') as f:
                json.dump(config, f)
                
            return True
        except Exception as e:
            logger.error(f"Error saving config: {str(e)}")
            return False
    
    def connect(self, service_url=None, force_reconnect=False):
        """
        Connect to the cloud service
        
        Args:
            service_url (str, optional): Override the service URL
            force_reconnect (bool): Force a new connection even if already connected
            
        Returns:
            bool: True if connection successful, False otherwise
        """
        if service_url:
            self.service_url = service_url
            
        # If already connected and not forcing reconnect, just return success
        if self.connected and not force_reconnect:
            return True
            
        # Disconnect any existing connection first
        if self.connected:
            self.disconnect()
        
        try:
            # Register with the service
            response = requests.post(
                f"{self.service_url}/register",
                json={"telegram_id": self.telegram_id},
                timeout=10
            )
            
            if response.status_code != 200:
                logger.error(f"Error connecting to service: {response.text}")
                return False
            
            data = response.json()
            if data.get('status') != 'success':
                logger.error(f"Error connecting to service: {data.get('message')}")
                return False
            
            # Store connection ID
            self.connection_id = data.get('connection_id')
            self._save_config()
            
            # Start polling for new screenshots
            self.connected = True
            self.stop_event.clear()
            self.reconnect_attempts = 0  # Reset reconnect attempts counter
            self.polling_thread = threading.Thread(target=self._polling_loop)
            self.polling_thread.daemon = True
            self.polling_thread.start()
            
            logger.info(f"Connected to service with connection ID: {self.connection_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error connecting to service: {str(e)}")
            return False
    
    def disconnect(self):
        """Disconnect from the cloud service"""
        self.connected = False
        self.stop_event.set()
        if self.polling_thread and self.polling_thread.is_alive():
            self.polling_thread.join(timeout=2)
        logger.info("Disconnected from service")
    
    def _should_attempt_reconnect(self):
        """Determine if reconnection should be attempted based on attempt count"""
        if self.reconnect_attempts >= self.max_reconnect_attempts:
            logger.warning(f"Maximum reconnection attempts ({self.max_reconnect_attempts}) reached. Giving up.")
            return False
        return True
        
    def _calculate_reconnect_delay(self):
        """Calculate delay time for reconnection with exponential backoff and jitter"""
        # Exponential backoff
        delay = min(
            self.reconnect_max_delay,
            pow(self.reconnect_backoff_base, min(self.reconnect_attempts, 6))  # Cap the exponent to avoid extremely long delays
        )
        
        # Add jitter (±jitter%)
        jitter_factor = 1.0 + (random.random() * self.reconnect_jitter * 2) - self.reconnect_jitter
        delay = delay * jitter_factor
        
        return delay
        
    def _handle_connection_error(self, error_message):
        """Handle connection errors with potential reconnection"""
        logger.error(error_message)
        
        # Don't attempt reconnect if we're not supposed to be connected
        if not self.connected or self.stop_event.is_set():
            return False
            
        # Increment reconnect attempts
        self.reconnect_attempts += 1
        
        # Check if we should try to reconnect
        if not self._should_attempt_reconnect():
            logger.error("Reconnection attempts exhausted. Connection failed.")
            self.connected = False
            return False
            
        # Calculate delay with exponential backoff
        delay = self._calculate_reconnect_delay()
        
        logger.info(f"Connection error detected. Attempting reconnect ({self.reconnect_attempts}/{self.max_reconnect_attempts}) in {delay:.2f} seconds...")
        
        # Wait before attempting reconnection
        time.sleep(delay)
        
        # Attempt reconnection
        return self.connect(force_reconnect=True)
    
    def _polling_loop(self):
        """Background thread to poll for new screenshots"""
        while not self.stop_event.is_set():
            try:
                # Check for new screenshots
                if self.connection_id:
                    # Ping the service
                    response = requests.post(
                        f"{self.service_url}/ping",
                        json={"connection_id": self.connection_id},
                        timeout=10
                    )
                    
                    if response.status_code != 200:
                        if self._handle_connection_error(f"Error polling service: {response.text}"):
                            continue  # Successfully reconnected, continue polling
                        else:
                            break  # Failed to reconnect, exit polling loop
                    
                    data = response.json()
                    if data.get('status') != 'success':
                        # Check specifically for invalid connection_id
                        if data.get('message') == 'Invalid connection_id':
                            if self._handle_connection_error("Error polling service: Invalid connection_id"):
                                continue  # Successfully reconnected, continue polling
                            else:
                                break  # Failed to reconnect, exit polling loop
                        else:
                            logger.error(f"Error polling service: {data.get('message')}")
                            time.sleep(self.polling_interval)
                            continue
                    
                    # Connection is working, reset reconnect attempts
                    self.reconnect_attempts = 0
                    
                    # Check if there are pending screenshots
                    if data.get('has_pending_screenshots'):
                        self._fetch_screenshots()
            
            except requests.RequestException as e:
                # Network-related errors should trigger reconnection
                if self._handle_connection_error(f"Network error in polling loop: {str(e)}"):
                    continue
                else:
                    break
            except Exception as e:
                # Other errors should be logged but not necessarily trigger reconnection
                logger.error(f"Error in polling loop: {str(e)}")
            
            # Wait for next poll
            time.sleep(self.polling_interval)
    
    def _fetch_screenshots(self):
        """Fetch pending screenshots from the service"""
        try:
            response = requests.post(
                f"{self.service_url}/fetch",
                json={"connection_id": self.connection_id},
                timeout=30  # Longer timeout for downloading screenshots
            )
            
            if response.status_code != 200:
                logger.error(f"Error fetching screenshots: {response.text}")
                return
            
            data = response.json()
            if data.get('status') != 'success':
                # Check specifically for invalid connection_id
                if data.get('message') == 'Invalid connection_id':
                    self._handle_connection_error("Error fetching screenshots: Invalid connection_id")
                else:
                    logger.error(f"Error fetching screenshots: {data.get('message')}")
                return
            
            # Process screenshots
            screenshots = data.get('screenshots', [])
            logger.info(f"Received {len(screenshots)} new screenshots")
            
            for screenshot in screenshots:
                try:
                    # Decode base64 image data
                    image_data = base64.b64decode(screenshot['data'])
                    
                    # Generate timestamp and filename
                    timestamp = screenshot.get('timestamp', datetime.now().isoformat())
                    file_type = screenshot.get('file_type', 'png')
                    
                    # Convert to Python datetime
                    dt = datetime.fromisoformat(timestamp)
                    # Format for filename including milliseconds
                    formatted_timestamp = dt.strftime("%d-%m-%Y---%H-%M-%S-%f")
                    
                    # Save screenshot to file
                    from modules.utils import get_screenshot_path, load_history, save_history
                    file_path = get_screenshot_path(formatted_timestamp)
                    
                    # Ensure screenshots directory exists
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    
                    # Save image
                    with open(file_path, 'wb') as f:
                        f.write(image_data)
                    
                    logger.info(f"Saved screenshot to {file_path}")
                    
                    # Add to history
                    history = load_history()
                    history.append({
                        "timestamp": formatted_timestamp,
                        "path": file_path
                    })
                    save_history(history)
                    
                    # Copy to clipboard
                    try:
                        self._copy_to_clipboard(file_path)
                        logger.info("Screenshot copied to clipboard")
                    except Exception as e:
                        logger.error(f"Failed to copy to clipboard: {str(e)}")
                    
                    # Call callback if provided
                    if self.callback:
                        self.callback(file_path, formatted_timestamp)
                        
                except Exception as e:
                    logger.error(f"Error processing screenshot: {str(e)}")
        
        except Exception as e:
            logger.error(f"Error fetching screenshots: {str(e)}")
    
    def _copy_to_clipboard(self, image_path):
        """Copy an image to the clipboard based on the OS."""
        import platform
        
        try:
            if platform.system() == 'Windows':
                # Windows clipboard handling
                import win32clipboard
                from PIL import Image
                import io
                
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
                # macOS clipboard handling using osascript
                import subprocess
                script = f'set the clipboard to (read (POSIX file "{image_path}") as picture)'
                subprocess.run(['osascript', '-e', script], check=True)
                
            elif platform.system() == 'Linux':
                # Linux clipboard handling using xclip
                import subprocess
                subprocess.run(['xclip', '-selection', 'clipboard', '-t', 'image/png', '-i', image_path], check=True)
                
            return True
            
        except Exception as e:
            logger.error(f"Clipboard error: {str(e)}")
            raise
    
    def update_service_url(self, url):
        """Update the service URL"""
        self.service_url = url
        self._save_config()
        
    def get_connection_status(self):
        """Get the current connection status"""
        return {
            "connected": self.connected,
            "connection_id": self.connection_id,
            "service_url": self.service_url,
            "reconnect_attempts": self.reconnect_attempts
        } 