import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import numpy as np

class FuturisticTheme:
    """Apply a sleek, futuristic theme to the SDF visualizer"""
    
    # Futuristic color palette
    COLORS = {
        'bg_dark': '#0D1117',
        'bg_medium': '#161B22',
        'bg_light': '#21262D',
        'accent': '#58A6FF',
        'accent_dark': '#1158C7',
        'highlight': '#39D353',
        'text': '#E6EDF3',
        'text_dim': '#8B949E',
        'warning': '#F85149',
        'grid': '#30363D',
    }
    
    # Visualization color schemes
    COLORMAPS = {
        'futuristic': {
            'inside': '#58A6FF',  # Blue
            'boundary': '#E6EDF3', # White
            'outside': '#F85149'   # Red
        },
        'neon': {
            'inside': '#39D353',   # Neon green
            'boundary': '#E6EDF3', # White
            'outside': '#D867FF'   # Neon purple
        },
        'cyberpunk': {
            'inside': '#FFC857',   # Yellow
            'boundary': '#E6EDF3', # White
            'outside': '#00CCFF'   # Cyan
        },
        'matrix': {
            'inside': '#00FF41',   # Matrix green
            'boundary': '#0FFF50', # Lighter green
            'outside': '#003B00'   # Dark green
        },
        'tron': {
            'inside': '#23FFDC',   # Teal
            'boundary': '#E6EDF3', # White
            'outside': '#FF56A9'   # Pink
        }
    }
    
    @staticmethod
    def apply_theme(root):
        """Apply the futuristic theme to the Tkinter application"""
        # Create a custom theme
        style = ttk.Style(root)
        
        # Check if theme already exists
        if 'futuristic' in style.theme_names():
            style.theme_use("futuristic")
            return
        
        # Configure the theme
        style.theme_create("futuristic", parent="alt", settings={
            "TFrame": {
                "configure": {
                    "background": FuturisticTheme.COLORS['bg_dark'],
                    "borderwidth": 0,
                }
            },
            "TLabelframe": {
                "configure": {
                    "background": FuturisticTheme.COLORS['bg_medium'],
                    "foreground": FuturisticTheme.COLORS['text'],
                    "borderwidth": 1,
                    "relief": "solid",
                    "bordercolor": FuturisticTheme.COLORS['accent'],
                }
            },
            "TLabelframe.Label": {
                "configure": {
                    "background": FuturisticTheme.COLORS['bg_medium'],
                    "foreground": FuturisticTheme.COLORS['accent'],
                    "font": ('Arial', 10, 'bold'),
                }
            },
            "TLabel": {
                "configure": {
                    "background": FuturisticTheme.COLORS['bg_medium'],
                    "foreground": FuturisticTheme.COLORS['text'],
                    "font": ('Arial', 9),
                }
            },
            "TButton": {
                "configure": {
                    "background": FuturisticTheme.COLORS['accent'],
                    "foreground": FuturisticTheme.COLORS['text'],
                    "borderwidth": 0,
                    "focusthickness": 0,
                    "focuscolor": FuturisticTheme.COLORS['accent'],
                    "padding": (10, 5),
                    "font": ('Arial', 9, 'bold'),
                },
                "map": {
                    "background": [("active", FuturisticTheme.COLORS['accent_dark'])],
                    "relief": [("pressed", "flat"), ("!pressed", "flat")],
                }
            },
            "TRadiobutton": {
                "configure": {
                    "background": FuturisticTheme.COLORS['bg_medium'],
                    "foreground": FuturisticTheme.COLORS['text'],
                    "indicatorcolor": FuturisticTheme.COLORS['bg_light'],
                    "font": ('Arial', 9),
                },
                "map": {
                    "indicatorcolor": [("selected", FuturisticTheme.COLORS['accent'])],
                }
            },
            "TEntry": {
                "configure": {
                    "background": FuturisticTheme.COLORS['bg_light'],
                    "foreground": FuturisticTheme.COLORS['text'],
                    "bordercolor": FuturisticTheme.COLORS['accent'],
                    "lightcolor": FuturisticTheme.COLORS['bg_light'],
                    "darkcolor": FuturisticTheme.COLORS['bg_light'],
                    "fieldbackground": FuturisticTheme.COLORS['bg_light'],
                    "font": ('Arial', 9),
                }
            },
            "Listbox": {
                "configure": {
                    "background": FuturisticTheme.COLORS['bg_light'],
                    "foreground": FuturisticTheme.COLORS['text'],
                    "borderwidth": 1,
                    "bordercolor": FuturisticTheme.COLORS['accent'],
                    "font": ('Arial', 9),
                }
            },
            "TScrollbar": {
                "configure": {
                    "background": FuturisticTheme.COLORS['bg_light'],
                    "troughcolor": FuturisticTheme.COLORS['bg_dark'],
                    "bordercolor": FuturisticTheme.COLORS['bg_dark'],
                }
            }
        })
        
        # Set the created theme
        style.theme_use("futuristic")
        
        # Configure Tkinter root and other non-ttk widgets
        root.configure(background=FuturisticTheme.COLORS['bg_dark'])
        
        # Configure standard Tkinter widgets that ttk doesn't cover
        root.option_add('*Listbox.background', FuturisticTheme.COLORS['bg_light'])
        root.option_add('*Listbox.foreground', FuturisticTheme.COLORS['text'])
        root.option_add('*Listbox.selectBackground', FuturisticTheme.COLORS['accent'])
        root.option_add('*Listbox.selectForeground', FuturisticTheme.COLORS['text'])
        
    @staticmethod
    def configure_matplotlib_style():
        """Configure matplotlib to use a futuristic style"""
        plt.style.use('dark_background')
        
        # Create custom futuristic matplotlib style
        plt.rcParams['figure.facecolor'] = FuturisticTheme.COLORS['bg_dark']
        plt.rcParams['axes.facecolor'] = FuturisticTheme.COLORS['bg_medium']
        plt.rcParams['axes.edgecolor'] = FuturisticTheme.COLORS['grid']
        plt.rcParams['axes.labelcolor'] = FuturisticTheme.COLORS['text']
        plt.rcParams['axes.grid'] = True
        plt.rcParams['grid.color'] = FuturisticTheme.COLORS['grid']
        plt.rcParams['grid.linestyle'] = ':'
        plt.rcParams['grid.alpha'] = 0.6
        plt.rcParams['xtick.color'] = FuturisticTheme.COLORS['text_dim']
        plt.rcParams['ytick.color'] = FuturisticTheme.COLORS['text_dim']
        plt.rcParams['text.color'] = FuturisticTheme.COLORS['text']
        plt.rcParams['font.family'] = 'monospace'
        
       
    @staticmethod
    def get_colormap(scheme='futuristic'):
        """Get a futuristic colormap for SDF visualization"""
        if scheme not in FuturisticTheme.COLORMAPS:
            scheme = 'futuristic'
            
        colors = [
            FuturisticTheme.COLORMAPS[scheme]['inside'],
            FuturisticTheme.COLORMAPS[scheme]['boundary'],
            FuturisticTheme.COLORMAPS[scheme]['outside']
        ]
        
        return LinearSegmentedColormap.from_list(f"sdf_{scheme}", colors, N=100)
    
    @staticmethod
    def add_glow_effect(ax, sdf, levels=0):
        """Add a glow effect to the SDF boundary"""
        # Create a glow effect around the zero level set
        glow = np.exp(-np.abs(sdf) * 5)
        
        # Apply the glow effect
        if isinstance(levels, (int, float)):
            levels = [levels]
            
        for level in levels:
            mask = np.abs(sdf - level) < 0.1
            if np.any(mask):
                # Draw glow with gradient alpha
                for i, alpha in enumerate(np.linspace(0.7, 0, 10)):
                    width = 4 - i * 0.3
                    ax.contour(
                        sdf, 
                        levels=[level], 
                        colors=[FuturisticTheme.COLORS['accent']], 
                        linewidths=width,
                        alpha=alpha
                    )
    
    @staticmethod
    def add_grid_lines(ax, spacing=1.0, line_style=':', alpha=0.2):
        """Add futuristic grid lines to the plot"""
        # Get axis limits
        xmin, xmax = ax.get_xlim()
        ymin, ymax = ax.get_ylim()
        
        # Round to nearest spacing
        xmin = np.floor(xmin / spacing) * spacing
        xmax = np.ceil(xmax / spacing) * spacing
        ymin = np.floor(ymin / spacing) * spacing
        ymax = np.ceil(ymax / spacing) * spacing
        
        # Create grid lines
        x_lines = np.arange(xmin, xmax + spacing, spacing)
        y_lines = np.arange(ymin, ymax + spacing, spacing)
        
        # Draw the grid lines
        for x in x_lines:
            ax.axvline(x=x, color=FuturisticTheme.COLORS['grid'], 
                      linestyle=line_style, alpha=alpha)
        
        for y in y_lines:
            ax.axhline(y=y, color=FuturisticTheme.COLORS['grid'], 
                      linestyle=line_style, alpha=alpha)
            
        # Add coordinate labels at intersections
        for x in x_lines:
            for y in y_lines:
                if x == 0 and y == 0:
                    # Highlight the origin
                    ax.plot(x, y, 'o', color=FuturisticTheme.COLORS['accent'], 
                           markersize=4, alpha=0.8)
                elif x == 0 or y == 0:
                    # Highlight the axes
                    ax.plot(x, y, '.', color=FuturisticTheme.COLORS['text_dim'], 
                           markersize=2, alpha=0.5)
    
    @staticmethod
    def add_coordinate_display(fig, ax):
        """Add a coordinate display that updates with mouse position"""
        coord_text = ax.text(
            0.02, 0.02, "x: 0.00, y: 0.00, d: 0.00", 
            transform=ax.transAxes,
            fontsize=9,
            family='monospace',
            color=FuturisticTheme.COLORS['text_dim'],
            bbox=dict(
                facecolor=FuturisticTheme.COLORS['bg_dark'],
                alpha=0.7,
                edgecolor=FuturisticTheme.COLORS['grid'],
                boxstyle='round,pad=0.5'
            )
        )
        
        # Store the SDF data for access by the event handler
        ax.sdf_data = None
        
        def update_coords(event):
            if event.inaxes == ax:
                x, y = event.xdata, event.ydata
                distance = 0
                
                # Get distance from SDF if available
                if ax.sdf_data is not None:
                    # Convert display coordinates to SDF grid indices
                    grid_x = int((x - ax.sdf_extent[0]) / (ax.sdf_extent[1] - ax.sdf_extent[0]) * ax.sdf_data.shape[1])
                    grid_y = int((y - ax.sdf_extent[2]) / (ax.sdf_extent[3] - ax.sdf_extent[2]) * ax.sdf_data.shape[0])
                    
                    # Ensure indices are within bounds
                    grid_x = max(0, min(grid_x, ax.sdf_data.shape[1] - 1))
                    grid_y = max(0, min(grid_y, ax.sdf_data.shape[0] - 1))
                    
                    distance = ax.sdf_data[grid_y, grid_x]
                    
                # Update the text
                coord_text.set_text(f"x: {x:.2f}, y: {y:.2f}, d: {distance:.2f}")
                fig.canvas.draw_idle()
        
        # Connect the event handler
        fig.canvas.mpl_connect('motion_notify_event', update_coords)
        
        return coord_text