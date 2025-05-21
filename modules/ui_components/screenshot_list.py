import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from customtkinter import CTkImage
from PIL import Image
import os

from modules.utils import save_history
from modules.clipboard import copy_to_clipboard

class ScreenshotList:
    """Component that displays and manages the list of screenshots"""
    
    def __init__(self, parent, bot=None, update_status_callback=None):
        self.parent = parent
        self.bot = bot
        self.update_status_callback = update_status_callback
        self.history = []
        self.screenshot_frame = None
        self.search_query = ""
        
        self._create_ui()
        
    def _create_ui(self):
        """Create the screenshot list UI components"""
        # Create a titled frame for screenshots - more compact
        list_container = ctk.CTkFrame(self.parent, corner_radius=10, fg_color="#F5F7F9", border_width=1, border_color="#E0E6ED")
        list_container.pack(fill="both", expand=True, pady=(0, 10))  # Reduced padding
        
        # Title for the screenshots section - smaller
        list_title = ctk.CTkLabel(
            list_container,
            text="Screenshots",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#333333"
        )
        list_title.pack(anchor="w", padx=12, pady=(10, 5))  # Reduced padding
        
        # Screenshot scrollable area with improved styling - more compact
        main_frame = ctk.CTkFrame(list_container, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=12, pady=(0, 10))  # Reduced padding
        
        # Style the scrollbar
        style = ttk.Style()
        style.theme_use('default')
        style.configure("Vertical.TScrollbar", background="#DDDDDD", bordercolor="#CCCCCC", 
                       arrowcolor="#666666", troughcolor="#F0F0F0")
        
        # Create a canvas with scrollbar
        canvas = tk.Canvas(main_frame, bg="#F5F7F9", bd=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview, style="Vertical.TScrollbar")
        self.screenshot_frame = ctk.CTkFrame(canvas, fg_color="#F5F7F9", corner_radius=0)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        
        canvas_frame = canvas.create_window((0, 0), window=self.screenshot_frame, anchor="nw")
        
        # Configure canvas and frame
        def configure_canvas(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(canvas_frame, width=event.width)
        
        self.screenshot_frame.bind("<Configure>", configure_canvas)
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(canvas_frame, width=e.width))
        
        # Add mouse wheel scrolling
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        
    def update_list(self, history=None, query=""):
        """Update the screenshot list with the provided history, filtered by query"""
        # Update history if provided
        if history is not None:
            self.history = history
            
        # Update search query
        self.search_query = query
            
        # Clear all existing widgets in the frame
        for widget in self.screenshot_frame.winfo_children():
            widget.destroy()
            
        # No screenshots message
        if not self.history:
            no_screenshots_label = ctk.CTkLabel(
                self.screenshot_frame, 
                text="No screenshots yet. Send photos via Telegram to get started!",
                font=ctk.CTkFont(size=12),  # Smaller font
                text_color="#666666"
            )
            no_screenshots_label.pack(pady=30)  # Reduced padding
            return
            
        # Sort history by timestamp (newest first)
        sorted_history = sorted(self.history, 
                               key=lambda x: x['timestamp'], 
                               reverse=True)
        
        # Filter by query if provided
        if query:
            sorted_history = [item for item in sorted_history 
                             if query.lower() in item['timestamp'].lower() or 
                                query.lower() in item['path'].lower()]
            
            # Show message if no results found
            if not sorted_history:
                no_results_label = ctk.CTkLabel(
                    self.screenshot_frame, 
                    text=f"No screenshots found matching '{query}'",
                    font=ctk.CTkFont(size=12),  # Smaller font
                    text_color="#666666"
                )
                no_results_label.pack(pady=30)  # Reduced padding
                return
        
        # Create a frame for each screenshot with thumbnail + info + buttons
        for i, item in enumerate(sorted_history):
            try:
                # Enhanced item frame with hover effect and better styling - more compact
                item_frame = ctk.CTkFrame(
                    self.screenshot_frame,
                    fg_color="#FFFFFF", 
                    corner_radius=6,  # Smaller corner radius
                    border_width=1,
                    border_color="#E0E6ED"
                )
                item_frame.pack(fill="x", padx=4, pady=3, ipady=5)  # Reduced padding
                
                # Try to load and display the thumbnail - smaller
                try:
                    img = Image.open(item['path'])
                    img.thumbnail((80, 80))  # Smaller thumbnail
                    photo = CTkImage(light_image=img, dark_image=img, size=(80, 80))
                    img_container = ctk.CTkFrame(item_frame, fg_color="#F0F0F0", corner_radius=4)  # Smaller corner radius
                    img_container.pack(side="left", padx=8)  # Reduced padding
                    
                    img_label = ctk.CTkLabel(img_container, image=photo, text="")
                    img_label._image = photo  # Keep a reference to prevent garbage collection
                    img_label.pack(padx=4, pady=4)  # Reduced padding
                except Exception as e:
                    img_label = ctk.CTkLabel(
                        item_frame, 
                        text="[No Preview]", 
                        width=80,  # Smaller width
                        height=80,  # Smaller height
                        fg_color="#F0F0F0",
                        corner_radius=4,  # Smaller corner radius
                        text_color="#666666"
                    )
                    img_label.pack(side="left", padx=8)  # Reduced padding
                
                # Info frame with better layout - more compact
                info_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
                
                display_time = item['timestamp']
                
                # Timestamp with better styling - smaller
                time_label = ctk.CTkLabel(
                    info_frame, 
                    text=f"Time: {display_time}", 
                    font=ctk.CTkFont(size=12, weight="bold"),  # Smaller font
                    anchor="w",
                    text_color="#333333"
                )
                time_label.pack(fill="x", anchor="w", pady=(4, 1))  # Reduced padding
                
                # Path with better styling - smaller
                path_label = ctk.CTkLabel(
                    info_frame, 
                    text=f"Path: {item['path']}", 
                    font=ctk.CTkFont(size=10),  # Smaller font
                    anchor="w",
                    text_color="#666666"
                )
                path_label.pack(fill="x", anchor="w")
                info_frame.pack(side="left", fill="both", expand=True, padx=5)
                
                # Buttons frame with modern styling - more compact
                button_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
                
                # Copy button with improved styling - smaller
                copy_button = ctk.CTkButton(
                    button_frame, 
                    text="Copy", 
                    command=lambda path=item['path']: self.copy_screenshot(path),
                    width=70,  # Smaller width
                    height=28,  # Smaller height
                    corner_radius=6,  # Smaller corner radius
                    font=ctk.CTkFont(size=11),  # Smaller font
                    hover_color="#0078D4",
                    fg_color="#0096FF"
                )
                copy_button.pack(pady=1)  # Reduced padding
                
                # Delete button with warning color - smaller
                delete_button = ctk.CTkButton(
                    button_frame, 
                    text="Delete", 
                    command=lambda idx=i, path=item['path']: self.delete_screenshot(idx, path),
                    width=70,  # Smaller width
                    height=28,  # Smaller height
                    corner_radius=6,  # Smaller corner radius
                    font=ctk.CTkFont(size=11),  # Smaller font
                    fg_color="#D32F2F",
                    hover_color="#B71C1C"
                )
                delete_button.pack(pady=1)  # Reduced padding
                
                button_frame.pack(side="right", padx=8)  # Reduced padding
                
            except Exception as e:
                print(f"Error displaying screenshot {i}: {e}")
    
    def copy_screenshot(self, path):
        """Copy a screenshot to clipboard."""
        try:
            copy_to_clipboard(path)
            if self.update_status_callback:
                self.update_status_callback(f"Copied: {os.path.basename(path)}")
        except Exception as e:
            if self.update_status_callback:
                self.update_status_callback(f"Error copying: {str(e)}")
            
    def delete_screenshot(self, idx, path):
        """Delete a screenshot."""
        try:
            # Delete the file
            if os.path.exists(path):
                os.remove(path)
                
            # Remove from history
            self.history = [item for item in self.history if item['path'] != path]
            save_history(self.history)
            
            # Update bot's history
            if self.bot:
                self.bot.set_history(self.history)
                
            # Update UI
            self.update_list(query=self.search_query)
            
            if self.update_status_callback:
                self.update_status_callback(f"Deleted: {os.path.basename(path)}")
        except Exception as e:
            if self.update_status_callback:
                self.update_status_callback(f"Error deleting: {str(e)}")
    
    def delete_all_screenshots(self):
        """Delete all screenshots."""
        try:
            # Delete all files
            for item in self.history:
                if os.path.exists(item['path']):
                    os.remove(item['path'])
                    
            # Clear history
            self.history = []
            save_history(self.history)
            
            # Update bot's history
            if self.bot:
                self.bot.set_history(self.history)
                
            # Update UI
            self.update_list()
            
            if self.update_status_callback:
                self.update_status_callback("All screenshots deleted")
        except Exception as e:
            if self.update_status_callback:
                self.update_status_callback(f"Error deleting all: {str(e)}") 