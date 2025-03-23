import tkinter as tk
from tkinter import ttk
import time
import threading
import numpy as np
from PIL import Image, ImageTk, ImageDraw, ImageFilter, ImageEnhance, ImageFont
import random
import math

class TronTheme:
    """Tron-inspired theme with neon green as primary color"""
    
    # Tron color palette
    COLORS = {
        'bg_dark': '#000800',          # Nearly black with slight green tint
        'bg_medium': '#001200',        # Very dark green
        'grid': '#002000',             # Slightly lighter dark green
        'neon': '#00FF41',             # Bright neon green (primary)
        'neon_dark': '#00A020',        # Darker neon green
        'neon_light': '#80FF80',       # Lighter neon green
        'accent': '#00FFFF',           # Cyan accent
        'glow': '#40FF40',             # Glow effect color
        'text': '#FFFFFF',             # White text
        'text_dim': '#60A080'          # Dimmed text
    }

class TronSplashScreen:
    def __init__(self, root, duration=3.0, callback=None):
        self.root = root
        self.duration = duration
        self.callback = callback
        
        # Store original window attributes to restore later
        self.original_attributes = {
            'title': root.title(),
            'geometry': root.geometry(),
            'attributes': {attr: root.attributes(attr) for attr in ['-alpha', '-topmost', '-fullscreen']}
        }
        
        # Configure root for splash screen
        root.title("SDF Visualizer")
        root.attributes('-alpha', 0.0)  # Start transparent
        root.attributes('-topmost', True)
        
        # Get screen dimensions
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        
        # Calculate window size (70% of screen)
        window_width = int(screen_width * 0.7)
        window_height = int(screen_height * 0.7)
        
        # Center the window
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        # Set window position and size
        root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Make window background black
        root.configure(background=TronTheme.COLORS['bg_dark'])
        
        # Create main frame
        self.frame = ttk.Frame(root, padding=0)
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        # Create canvas for animation
        self.canvas = tk.Canvas(
            self.frame, 
            bg=TronTheme.COLORS['bg_dark'],
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Create animated elements
        self.create_splash_elements()
        
        # Start animation
        self.start_time = time.time()
        self.animate()
    
    def create_splash_elements(self):
        """Create the animated elements for the splash screen with Tron theme"""
        # Get canvas dimensions - wait for window to be drawn
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        
        # If dimensions are too small, use fallback values
        if width < 10 or height < 10:  # Not properly initialized
            width = int(self.root.winfo_screenwidth() * 0.7)
            height = int(self.root.winfo_screenheight() * 0.7)
        
        # Configure canvas to fill the window
        self.canvas.config(width=width, height=height)
        
        # Calculate center positions
        self.center_x = width // 2
        self.center_y = height // 2
        
        # Create background with grid
        self.bg_image = self.create_tron_background(width, height)
        self.bg_photo = ImageTk.PhotoImage(self.bg_image)
        self.bg_id = self.canvas.create_image(self.center_x, self.center_y, image=self.bg_photo)
        
        # Create circular elements
        self.circles = []
        for i in range(3):
            radius = 80 + i * 40
            circle = self.canvas.create_oval(
                self.center_x - radius, self.center_y - radius,
                self.center_x + radius, self.center_y + radius,
                outline=TronTheme.COLORS['neon'],
                width=2,
                fill=""
            )
            self.circles.append(circle)
        
        # Create hexagon logo
        self.hexagon_points = self.calculate_hexagon(self.center_x, self.center_y, 100)
        self.hexagon = self.canvas.create_polygon(
            self.hexagon_points,
            outline=TronTheme.COLORS['neon'],
            fill=TronTheme.COLORS['bg_medium'],
            width=2
        )
        
        # Add inner hexagon
        inner_points = self.calculate_hexagon(self.center_x, self.center_y, 70)
        self.inner_hexagon = self.canvas.create_polygon(
            inner_points,
            outline=TronTheme.COLORS['neon'],
            fill="",
            width=1
        )
        
        # Add title text with glow effect
        # First create shadow/glow
        for i in range(3, 0, -1):
            offset = i * 2
            alpha = 0.3 - i * 0.05
            # Create a version of the neon color with reduced brightness for glow
            glow_color = self.hex_with_opacity(TronTheme.COLORS['glow'], alpha)
            self.canvas.create_text(
                self.center_x, self.center_y - 10,
                text="SDF VISUALIZER",
                font=('Arial', 36, 'bold'),
                fill=glow_color
            )
        
        # Main title
        self.title_id = self.canvas.create_text(
            self.center_x, self.center_y - 10,
            text="SDF VISUALIZER",
            font=('Arial', 36, 'bold'),
            fill=TronTheme.COLORS['neon']
        )
        
        # Add subtitle
        self.subtitle_id = self.canvas.create_text(
            self.center_x, self.center_y + 30,
            text="SIGNED DISTANCE FIELD",
            font=('Arial', 14),
            fill=TronTheme.COLORS['text']
        )
        
        # Add loading bar
        bar_width = width * 0.4
        bar_height = 6
        bar_left = self.center_x - bar_width/2
        bar_right = self.center_x + bar_width/2
        bar_top = self.center_y + 80
        bar_bottom = bar_top + bar_height
        
        # Create loading bar background with double border
        self.canvas.create_rectangle(
            bar_left - 3, bar_top - 3,
            bar_right + 3, bar_bottom + 3,
            fill=TronTheme.COLORS['bg_dark'],
            outline=TronTheme.COLORS['neon_dark'],
            width=1
        )
        
        self.loading_bg_id = self.canvas.create_rectangle(
            bar_left, bar_top,
            bar_right, bar_bottom,
            fill=TronTheme.COLORS['bg_medium'],
            outline=TronTheme.COLORS['neon'],
            width=1
        )
        
        self.loading_bar_id = self.canvas.create_rectangle(
            bar_left, bar_top,
            bar_left, bar_bottom,  # Initially empty
            fill=TronTheme.COLORS['neon'],
            outline=""
        )
        
        # Add glowing particles
        self.particles = []
        for _ in range(20):
            x = random.randint(0, width)
            y = random.randint(0, height)
            size = random.randint(1, 3)
            particle = self.canvas.create_oval(
                x-size, y-size, x+size, y+size,
                fill=TronTheme.COLORS['neon'],
                outline="",
                tags="particle"
            )
            self.particles.append({
                'id': particle,
                'x': x,
                'y': y,
                'vx': random.uniform(-1, 1),
                'vy': random.uniform(-1, 1),
                'size': size
            })
        
        # Add version text
        self.version_id = self.canvas.create_text(
            width - 20, height - 20,
            text="v1.0.0",
            font=('Arial', 9),
            fill=TronTheme.COLORS['text_dim'],
            anchor='se'
        )
        
        # Add "loading" text that changes
        self.loading_text_id = self.canvas.create_text(
            self.center_x, bar_bottom + 20,
            text="INITIALIZING...",
            font=('Arial', 10),
            fill=TronTheme.COLORS['text']
        )
    
    def calculate_hexagon(self, cx, cy, size):
        """Calculate hexagon points"""
        points = []
        for i in range(6):
            angle_deg = 60 * i - 30
            angle_rad = math.pi / 180 * angle_deg
            points.append(cx + size * math.cos(angle_rad))
            points.append(cy + size * math.sin(angle_rad))
        return points
    
    def create_tron_background(self, width, height):
        """Create a Tron-style grid background"""
        # Create base image with dark background
        image = Image.new('RGBA', (width, height), TronTheme.COLORS['bg_dark'])
        draw = ImageDraw.Draw(image)
        
        # Draw horizontal grid lines
        grid_spacing = 30
        for y in range(0, height, grid_spacing):
            # Main grid lines
            grid_color = self.hex_to_rgb(TronTheme.COLORS['grid'])
            grid_color = grid_color + (102,)  # Add alpha of 0.4 (102/255)
            draw.line([(0, y), (width, y)], fill=grid_color, width=1)
            
            # Dimmer subgrid lines
            if y % (grid_spacing * 4) == 0:
                neon_color = self.hex_to_rgb(TronTheme.COLORS['neon'])
                neon_color = neon_color + (51,)  # Add alpha of 0.2 (51/255)
                draw.line([(0, y), (width, y)], fill=neon_color, width=1)
        
        # Draw vertical grid lines
        for x in range(0, width, grid_spacing):
            # Main grid lines
            grid_color = self.hex_to_rgb(TronTheme.COLORS['grid'])
            grid_color = grid_color + (102,)  # Add alpha of 0.4 (102/255)
            draw.line([(x, 0), (x, height)], fill=grid_color, width=1)
            
            # Brighter main grid lines
            if x % (grid_spacing * 4) == 0:
                neon_color = self.hex_to_rgb(TronTheme.COLORS['neon'])
                neon_color = neon_color + (51,)  # Add alpha of 0.2 (51/255)
                draw.line([(x, 0), (x, height)], fill=neon_color, width=1)
        
        # Add horizontal glow line
        center_y = height // 2
        for i in range(5):
            alpha = 0.1 - i * 0.02
            if alpha <= 0:
                continue
            y_offset = grid_spacing * i
            alpha_int = int(alpha * 255)
            neon_color = self.hex_to_rgb(TronTheme.COLORS['neon'])
            neon_color = neon_color + (alpha_int,)
            draw.line([(0, center_y + y_offset), (width, center_y + y_offset)], fill=neon_color, width=2)
            draw.line([(0, center_y - y_offset), (width, center_y - y_offset)], fill=neon_color, width=2)
        
        # Apply slight blur
        image = image.filter(ImageFilter.GaussianBlur(radius=1))
        
        return image
    
    def hex_to_rgb(self, hex_color):
        """Convert hex color to rgb tuple"""
        h = hex_color.lstrip('#')
        return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
    
    def hex_with_opacity(self, hex_color, opacity=1.0):
        """Convert a hex color to a hex color with opacity for Tkinter"""
        # For Tkinter, we need to convert to a format like #RRGGBB
        # We'll simulate opacity by blending with the background color
        bg = self.hex_to_rgb(TronTheme.COLORS['bg_dark'])
        fg = self.hex_to_rgb(hex_color)
        
        # Blend the colors based on opacity
        r = int(bg[0] * (1 - opacity) + fg[0] * opacity)
        g = int(bg[1] * (1 - opacity) + fg[1] * opacity)
        b = int(bg[2] * (1 - opacity) + fg[2] * opacity)
        
        # Return as hex
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def animate(self):
        """Animate the splash screen"""
        current_time = time.time()
        elapsed = current_time - self.start_time
        progress = min(elapsed / self.duration, 1.0)
        
        # Update window alpha for fade-in
        if progress < 0.3:
            fade_in = progress / 0.3
            self.root.attributes('-alpha', fade_in)
        elif progress > 0.8:
            fade_out = (1.0 - progress) / 0.2
            self.root.attributes('-alpha', fade_out)
        
        # Update loading bar
        bar_coords = self.canvas.coords(self.loading_bg_id)
        bar_width = bar_coords[2] - bar_coords[0]
        bar_progress = bar_coords[0] + bar_width * progress
        self.canvas.coords(
            self.loading_bar_id,
            bar_coords[0], bar_coords[1],
            bar_progress, bar_coords[3]
        )
        
        # Rotate hexagon slightly
        angle = elapsed * 10  # 10 degrees per second
        new_points = self.calculate_hexagon(self.center_x, self.center_y, 100 + math.sin(elapsed*2) * 5)
        self.canvas.coords(self.hexagon, *new_points)
        
        # Pulse the circles
        for i, circle in enumerate(self.circles):
            pulse = 1 + 0.1 * math.sin(elapsed * 2 + i)
            radius = (80 + i * 40) * pulse
            self.canvas.coords(
                circle,
                self.center_x - radius, self.center_y - radius,
                self.center_x + radius, self.center_y + radius
            )
        
        # Update particles
        for particle in self.particles:
            # Update position
            particle['x'] += particle['vx'] * 2
            particle['y'] += particle['vy'] * 2
            
            # Bounce off edges
            if particle['x'] < 0 or particle['x'] > self.canvas.winfo_width():
                particle['vx'] *= -1
            if particle['y'] < 0 or particle['y'] > self.canvas.winfo_height():
                particle['vy'] *= -1
            
            # Update canvas object
            size = particle['size']
            self.canvas.coords(
                particle['id'],
                particle['x']-size, particle['y']-size,
                particle['x']+size, particle['y']+size
            )
            
            # Random color flicker
            alpha = 0.5 + 0.5 * math.sin(elapsed * 3 + particle['x'])
            if random.random() < 0.05:
                color = TronTheme.COLORS['accent'] if random.random() < 0.3 else TronTheme.COLORS['neon']
                self.canvas.itemconfig(particle['id'], fill=color)
        
        # Update loading text
        loading_texts = ["INITIALIZING...", "LOADING SHADERS...", "CALIBRATING...", "RENDERING GRID...", "OPTIMIZING..."]
        loading_index = int((elapsed * 2) % len(loading_texts))
        self.canvas.itemconfig(self.loading_text_id, text=loading_texts[loading_index])
        
        # Continue animation if not complete
        if progress < 1.0:
            self.root.after(16, self.animate)  # ~60fps
        else:
            self.finish()
    
    def finish(self):
        """Finish the splash screen and restore original window"""
        # Clear canvas elements
        self.canvas.delete("all")
        self.frame.destroy()
        
        # Restore original window attributes
        self.root.title(self.original_attributes['title'])
        self.root.geometry(self.original_attributes['geometry'])
        for attr, value in self.original_attributes['attributes'].items():
            self.root.attributes(attr, value)
        
        # Execute callback function if provided
        if self.callback:
            # Use after method to avoid callback during animation
            self.root.after(100, self.callback)

def start_with_tron_splash(main_function):
    """Start the application with a Tron-themed splash screen"""
    root = tk.Tk()
    root.configure(background='black')
    
    # Create and run splash screen
    splash = TronSplashScreen(root, duration=3.0, callback=lambda: main_function(root))
    
    # Start the main loop
    root.mainloop()

# For testing
if __name__ == "__main__":
    def dummy_function(root):
        root.title("Main Application")
        label = tk.Label(root, text="Main App Started", font=('Arial', 24))
        label.pack(pady=20)
    
    start_with_tron_splash(dummy_function)