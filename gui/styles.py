import customtkinter as ctk

class AppStyles:
    COLORS = {
        'primary': '#1f6aa5',
        'primary_hover': '#155a8a',
        'secondary': '#2b2b2b',
        'background': '#1a1a1a',
        'surface': '#2d2d2d',
        'surface_hover': '#3d3d3d',
        'text': '#ffffff',
        'text_secondary': '#b0b0b0',
        'success': '#4CAF50',
        'warning': '#FF9800',
        'error': '#f44336',
        'info': '#2196F3'
    }
    
    @staticmethod
    def setup_theme():
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
    
    @staticmethod
    def get_font(size=14, weight="normal"):
        return ctk.CTkFont(family="Segoe UI", size=size, weight=weight)
    
    @staticmethod
    def create_card_frame(master, **kwargs):
        defaults = {
            'fg_color': AppStyles.COLORS['surface'],
            'corner_radius': 10,
            'border_width': 1,
            'border_color': '#404040'
        }
        defaults.update(kwargs)
        return ctk.CTkFrame(master, **defaults)