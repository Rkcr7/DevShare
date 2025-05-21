import customtkinter as ctk

class SearchPanel:
    """Component that handles the search functionality"""
    
    def __init__(self, parent, search_callback=None):
        self.parent = parent
        self.search_callback = search_callback
        self.search_entry = None
        
        self._create_ui()
        
    def _create_ui(self):
        """Create the search panel UI components"""
        # More compact search container
        search_container = ctk.CTkFrame(self.parent, corner_radius=10, fg_color="#F5F7F9", border_width=1, border_color="#E0E6ED")
        search_container.pack(fill="x")
        
        search_inner_frame = ctk.CTkFrame(search_container, fg_color="transparent")
        search_inner_frame.pack(fill="x", padx=12, pady=12)  # Reduced padding
        
        # Search label with better styling - more compact
        search_label = ctk.CTkLabel(
            search_inner_frame, 
            text="Search History:",
            font=ctk.CTkFont(size=12),  # Smaller font
            text_color="#333333"
        )
        search_label.pack(side="left")
        
        # Enhanced search entry with placeholder
        self.search_entry = ctk.CTkEntry(
            search_inner_frame, 
            width=200,  # Reduced width
            height=28,  # Reduced height
            corner_radius=6,  # Smaller corner radius
            border_width=1,
            border_color="#DDDDDD",
            fg_color="#FFFFFF",
            placeholder_text="Enter search term...",
            font=ctk.CTkFont(size=12)  # Smaller font
        )
        self.search_entry.pack(side="left", padx=10)
        
        # Better search button
        search_button = ctk.CTkButton(
            search_inner_frame, 
            text="Search",
            command=self.search,
            height=28,  # Reduced height
            width=70,  # Reduced width
            corner_radius=6,  # Smaller corner radius
            font=ctk.CTkFont(size=12),  # Smaller font
            hover_color="#0078D4"
        )
        search_button.pack(side="left")
        
        # Bind Enter key to search
        self.search_entry.bind("<Return>", lambda event: self.search())
        
    def search(self):
        """Search history based on the query in the search entry."""
        if self.search_callback:
            self.search_callback(self.search_entry.get())
            
    def get_query(self):
        """Get the current search query."""
        return self.search_entry.get() if self.search_entry else "" 