import tkinter as tk
from tkinter import ttk
import time
import threading
import numpy as np
from PIL import Image, ImageTk, ImageDraw, ImageFilter

from futuristic_theme import FuturisticTheme

class SplashScreen:
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
        
        # Calculate window size (60% of screen)
        window_width = int(screen_width * 0.6)
        window_height = int(screen_height * 0.6)
        
        # Center the window
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        # Set window position and size
        root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Create main frame
        self.frame = ttk.Frame(root, padding=0)
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        # Create canvas for animation
        self.canvas = tk.Canvas(
            self.frame, 
            bg=FuturisticTheme.COLORS['bg_dark'],
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Create animated elements
        self.create_splash_elements()
        
        # Start animation
        self.start_time = time.time()
        self.animate()
    
    def create_splash_elements(self):
        """Create the animated elements for the splash screen"""
        # Get canvas dimensions
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        
        # Create background with gradient
        self.bg_image = self.create_background(width, height)
        self.bg_photo = ImageTk.PhotoImage(self.bg_image)
        self.bg_id = self.canvas.create_image(width//2, height//2, image=self.bg_photo)
        
        # Add logo
        self.logo_image = self.create_logo(width//4, height//4)
        self.logo_photo = ImageTk.PhotoImage(self.logo_image)
        self.logo_id = self.canvas.create_image(width//2, height//2 - 50, image=self.logo_photo)
        
        # Add title text
        self.title_id = self.canvas.create_text(
            width//2, height//2 + 80,
            text="SDF VISUALIZER",
            font=('Arial', 24, 'bold'),
            fill=FuturisticTheme.COLORS['accent']
        )
        
        # Add subtitle
        self.subtitle_id = self.canvas.create_text(
            width//2, height//2 + 120,
            text="Signed Distance Field Visualization Tool",
            font=('Arial', 12),
            fill=FuturisticTheme.COLORS['text']
        )
        
        # Add loading bar
        self.loading_bg_id = self.canvas.create_rectangle(
            width//4, height//2 + 160,
            3*width//4, height//2 + 170,
            fill=FuturisticTheme.COLORS['bg_light'],
            outline=FuturisticTheme.COLORS['accent']
        )
        
        self.loading_bar_id = self.canvas.create_rectangle(
            width//4, height//2 + 160,
            width//4, height//2 + 170,
            fill=FuturisticTheme.COLORS['accent'],
            outline=""
        )
        
        # Add version text
        self.version_id = self.canvas.create_text(
            width - 20, height - 20,
            text="v1.0.0",
            font=('Arial', 9),
            fill=FuturisticTheme.COLORS['text_dim'],
            anchor='se'
        )
    
    def create_background(self, width, height):
        """Create a futuristic background image"""
        # Create base image with gradient
        image = Image.new('RGBA', (width, height), FuturisticTheme.COLORS['bg_dark'])
        draw = ImageDraw.Draw(image)
        
        # Add radial gradient
        for r in range(0, int(width * 0.8), 2):
            # Decrease alpha for outer circles
            alpha = int(255 * (1 - r / (width * 0.8)))
            if alpha <= 0:
                break
                
            color = self.hex_to_rgba(FuturisticTheme.COLORS['accent_dark'], alpha)
            draw.ellipse(
                [width//2 - r, height//2 - r, width//2 + r, height//2 + r],
                outline=color
            )
        
        # Add grid lines
        grid_color = self.hex_to_rgba(FuturisticTheme.COLORS['grid'], 40)
        grid_spacing = 30
        
        # Horizontal lines
        for y in range(0, height, grid_spacing):
            draw.line([(0, y), (width, y)], fill=grid_color, width=1)
        
        # Vertical lines
        for x in range(0, width, grid_spacing):
            draw.line([(x, 0), (x, height)], fill=grid_color, width=1)
        
        # Apply blur
        image = image.filter(ImageFilter.GaussianBlur(radius=3))
        
        return image
    
    def create_logo(self, width, height):
        """Create a futuristic SDF logo"""
        # Create base image
        image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # Draw a circle
        circle_color = self.hex_to_rgba(FuturisticTheme.COLORS['accent'], 230)
        draw.ellipse([width//4, height//4, 3*width//4, 3*height//4], outline=circle_color, width=3)
        
        # Draw a square
        square_color = self.hex_to_rgba(FuturisticTheme.COLORS['highlight'], 200)
        draw.rectangle([width//3, height//3, 2*width//3, 2*height//3], outline=square_color, width=3)
        
        # Add glow effect
        image = image.filter(ImageFilter.GaussianBlur(radius=5))
        
        # Redraw shapes with sharper edges
        draw = ImageDraw.Draw(image)
        draw.ellipse([width//4, height//4, 3*width//4, 3*height//4], outline=circle_color, width=2)
        draw.rectangle([width//3, height//3, 2*width//3, 2*height//3], outline=square_color, width=2)
        
        # Add SDF letters
        text_color = self.hex_to_rgba(FuturisticTheme.COLORS['text'], 255)
        draw.text((width//2, height//2), "SDF", fill=text_color, anchor="mm", font=None)
        
        return image
    
    def hex_to_rgba(self, hex_color, alpha):
        """Convert hex color to RGBA tuple"""
        h = hex_color.lstrip('#')
        rgb = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
        return rgb + (alpha,)
    
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
        width = self.root.winfo_width()
        bar_width = int(width//2 * progress)
        self.canvas.coords(
            self.loading_bar_id,
            width//4, self.canvas.coords(self.loading_bar_id)[1],
            width//4 + bar_width, self.canvas.coords(self.loading_bar_id)[3]
        )
        
        # Pulse the logo
        pulse = np.sin(elapsed * 4) * 0.1 + 0.9
        self.canvas.scale(self.logo_id, width//2, self.canvas.coords(self.logo_id)[1], pulse, pulse)
        
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

def start_with_splash(main_function):
    """Start the application with a splash screen"""
    root = tk.Tk()
    
    # Apply futuristic theme
    FuturisticTheme.apply_theme(root)
    
    # Create and run splash screen
    splash = SplashScreen(root, duration=2.5, callback=lambda: main_function(root))
    
    # Start the main loop
    root.mainloop()

if __name__ == "__main__":
    # Demo function to call after splash screen
    def demo_app(root):
        frame = ttk.Frame(root, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        ttk.Label(frame, text="Main Application", font=('Arial', 24, 'bold')).pack(pady=20)
        ttk.Button(frame, text="Exit", command=root.destroy).pack(pady=10)
    
    # Run the demo
    start_with_splash(demo_app)