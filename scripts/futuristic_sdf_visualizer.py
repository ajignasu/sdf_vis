import numpy as np
import copy
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.gridspec as gridspec
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.cm as cm
import tkinter as tk
from tkinter import ttk
from matplotlib.animation import FuncAnimation
import scipy.ndimage as ndimage

from futuristic_theme import FuturisticTheme
from advanced_visualization import AdvancedVisualization

class FuturisticSDFVisualizer:
    def __init__(self, root, resolution=200, domain_size=5.0):
        self.root = root
        self.root.title("Futuristic SDF Visualizer")
        self.resolution = resolution
        self.domain_size = domain_size
        self.update_grid()
        
        # Apply futuristic theme
        try:
            style = ttk.Style(root)
            if 'futuristic' not in style.theme_names():
                FuturisticTheme.apply_theme(root)
        except Exception as e:
            print(f"Note: Theme already applied or error: {e}")
        
        # Configure matplotlib style
        FuturisticTheme.configure_matplotlib_style()
        
        # Create a grid of x,y coordinates
        x = np.linspace(-domain_size, domain_size, resolution)
        y = np.linspace(-domain_size, domain_size, resolution)
        self.X, self.Y = np.meshgrid(x, y)
        
        # Initialize with some default shapes
        self.shapes = []
        self.active_shape_index = None
        self.boolean_operation = "none"
        
        # Initialize visualization settings
        self.visualization_style = "Standard"
        self.use_unsigned_sdf = False  # Add this flag for unsigned SDF
        self.animation_active = False
        self.animation = None
        
        # Initialize GUI
        self.setup_gui()
        
    def setup_gui(self):
        # Set up the main frame
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure the grid layout
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Create left panel for controls
        left_panel = ttk.Frame(main_frame, padding=5)
        left_panel.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        # Add title bar
        title_frame = ttk.Frame(left_panel)
        title_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        title_label = ttk.Label(title_frame, text="SDF Visualizer", font=('Arial', 14, 'bold'), 
                              foreground=FuturisticTheme.COLORS['accent'])
        title_label.grid(row=0, column=0, sticky=tk.W)
        
        # Create right panel for visualization
        right_panel = ttk.Frame(main_frame, padding=5)
        right_panel.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        # Configure weights
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=3)
        main_frame.rowconfigure(0, weight=1)
        
        # Create shape selection section
        shape_frame = ttk.LabelFrame(left_panel, text="ADD SHAPE", padding=5)
        shape_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Shape buttons with icons (using text for now, can replace with icons)
        self.create_button(shape_frame, "⭕ Circle", lambda: self.add_shape("circle"), 0)
        self.create_button(shape_frame, "⬛ Rectangle", lambda: self.add_shape("rectangle"), 1)
        self.create_button(shape_frame, "🔺 Triangle", lambda: self.add_shape("triangle"), 2)
        self.create_button(shape_frame, "📏 Line", lambda: self.add_shape("line"), 3)
        
        # Boolean operations section
        bool_frame = ttk.LabelFrame(left_panel, text="BOOLEAN OPERATION", padding=5)
        bool_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=5)
        
        self.bool_var = tk.StringVar(value="none")
        ttk.Radiobutton(bool_frame, text="None", variable=self.bool_var, value="none", 
                       command=self.update_boolean_op).grid(row=0, column=0, sticky=tk.W)
        ttk.Radiobutton(bool_frame, text="Union", variable=self.bool_var, value="union", 
                       command=self.update_boolean_op).grid(row=1, column=0, sticky=tk.W)
        ttk.Radiobutton(bool_frame, text="Intersection", variable=self.bool_var, value="intersection", 
                       command=self.update_boolean_op).grid(row=2, column=0, sticky=tk.W)
        ttk.Radiobutton(bool_frame, text="Difference", variable=self.bool_var, value="difference", 
                       command=self.update_boolean_op).grid(row=3, column=0, sticky=tk.W)
        ttk.Radiobutton(bool_frame, text="Smooth Union", variable=self.bool_var, value="smooth_union", 
                       command=self.update_boolean_op).grid(row=4, column=0, sticky=tk.W)
        
        # Drawing mode button
        drawing_frame = ttk.Frame(shape_frame)
        drawing_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=5)
        self.create_button(drawing_frame, "✏️ Draw Shape", self.toggle_drawing_mode, 0)

        # Drawing options that will be shown when in drawing mode
        self.drawing_options_frame = ttk.Frame(shape_frame)
        self.drawing_mode_active = False
        
        # Shape properties section
        self.properties_frame = ttk.LabelFrame(left_panel, text="SHAPE PROPERTIES", padding=5)
        self.properties_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Visualization style section
        viz_frame = ttk.LabelFrame(left_panel, text="VISUALIZATION", padding=5)
        viz_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Visualization style
        ttk.Label(viz_frame, text="Style:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.viz_style_var = tk.StringVar(value="Standard")
        style_combo = ttk.Combobox(viz_frame, textvariable=self.viz_style_var, 
                                 values=["Standard", "Hologram", "Neon", "Heatmap", "Electric"], 
                                 state="readonly", width=10)
        style_combo.grid(row=0, column=1, sticky=tk.W, pady=2)
        style_combo.bind("<<ComboboxSelected>>", self.update_visualization_style)
        

        viz_frame = ttk.LabelFrame(left_panel, text="VISUALIZATION", padding=5)
        viz_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Visualization style
        ttk.Label(viz_frame, text="Style:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.viz_style_var = tk.StringVar(value="Standard")
        style_combo = ttk.Combobox(viz_frame, textvariable=self.viz_style_var, 
                                values=["Standard", "Hologram", "Neon", "Heatmap", "Electric"], 
                                state="readonly", width=10)
        style_combo.grid(row=0, column=1, sticky=tk.W, pady=2)
        style_combo.bind("<<ComboboxSelected>>", self.update_visualization_style)
        
        # Unsigned SDF option
        self.unsigned_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(viz_frame, text="Unsigned Distance", variable=self.unsigned_var,
                    command=self.toggle_unsigned_sdf).grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        # Animation toggle
        self.anim_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(viz_frame, text="Animation", variable=self.anim_var,
                    command=self.toggle_animation).grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        # Resolution control
        ttk.Label(viz_frame, text="Resolution:").grid(row=4, column=0, sticky=tk.W, pady=2)
        resolution_frame = ttk.Frame(viz_frame)
        resolution_frame.grid(row=4, column=1, sticky=tk.W, pady=2)

        self.resolution_var = tk.IntVar(value=self.resolution)
        resolution_entry = ttk.Entry(resolution_frame, textvariable=self.resolution_var, width=5)
        resolution_entry.pack(side=tk.LEFT, padx=(0, 5))
        resolution_entry.bind("<Return>", self.update_resolution)

        # Preset resolution buttons
        ttk.Button(resolution_frame, text="100", command=lambda: self.set_resolution(100), 
                width=3).pack(side=tk.LEFT, padx=1)
        ttk.Button(resolution_frame, text="200", command=lambda: self.set_resolution(200), 
                width=3).pack(side=tk.LEFT, padx=1)
        ttk.Button(resolution_frame, text="400", command=lambda: self.set_resolution(400), 
                width=3).pack(side=tk.LEFT, padx=1)
        
        # Save button
        ttk.Button(viz_frame, text="Save Image", command=self.save_visualization).grid(
            row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Animation toggle
        self.anim_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(viz_frame, text="Animation", variable=self.anim_var,
                      command=self.toggle_animation).grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        # Shape list section
        shapes_frame = ttk.LabelFrame(left_panel, text="SHAPES", padding=5)
        shapes_frame.grid(row=5, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Listbox for shapes
        self.shapes_listbox = tk.Listbox(shapes_frame, height=5, bg=FuturisticTheme.COLORS['bg_light'],
                                      fg=FuturisticTheme.COLORS['text'], selectbackground=FuturisticTheme.COLORS['accent'],
                                      highlightthickness=1, highlightcolor=FuturisticTheme.COLORS['accent'])
        self.shapes_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.shapes_listbox.bind('<<ListboxSelect>>', self.on_shape_select)
        
        # Scrollbar for listbox
        shapes_scrollbar = ttk.Scrollbar(shapes_frame, orient=tk.VERTICAL, command=self.shapes_listbox.yview)
        shapes_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.shapes_listbox.configure(yscrollcommand=shapes_scrollbar.set)
        
        # Buttons for shape manipulation
        shape_button_frame = ttk.Frame(shapes_frame)
        shape_button_frame.grid(row=1, column=0, columnspan=2, sticky=tk.W)
        ttk.Button(shape_button_frame, text="Remove", command=self.remove_shape).grid(row=0, column=0, padx=2)
        ttk.Button(shape_button_frame, text="Clear All", command=self.clear_shapes).grid(row=0, column=1, padx=2)
        
        # Make listbox and shape frame expandable
        shapes_frame.rowconfigure(0, weight=1)
        shapes_frame.columnconfigure(0, weight=1)
        left_panel.rowconfigure(5, weight=1)
        left_panel.columnconfigure(0, weight=1)
        
        # Create the matplotlib figure for visualization
        self.fig = Figure(figsize=(8, 8), dpi=100, facecolor=FuturisticTheme.COLORS['bg_dark'])
        
        # SDF visualization
        self.ax_sdf = self.fig.add_subplot(111)
        self.ax_sdf.set_title("SDF Visualization", fontsize=12, color=FuturisticTheme.COLORS['text'])
        self.ax_sdf.set_aspect('equal')
        
        # Embed the matplotlib figure in tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=right_panel)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Add coordinate display
        FuturisticTheme.add_coordinate_display(self.fig, self.ax_sdf)
        
        # Initialize the plot
        self.update_plot()

    def toggle_drawing_mode(self):
        """Toggle between normal and drawing modes"""
        self.drawing_mode_active = not self.drawing_mode_active
        
        if self.drawing_mode_active:
            # Show drawing options
            self.drawing_options_frame.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=5)
            
            # Create drawing options if they don't exist yet
            if not hasattr(self, 'brush_size_var'):
                self.brush_size_var = tk.IntVar(value=5)
                self.smoothing_var = tk.BooleanVar(value=True)
                
                ttk.Label(self.drawing_options_frame, text="Brush Size:").grid(row=0, column=0, sticky=tk.W)
                ttk.Scale(self.drawing_options_frame, from_=1, to=20, variable=self.brush_size_var, 
                        orient=tk.HORIZONTAL).grid(row=0, column=1, sticky=(tk.W, tk.E))
                
                ttk.Checkbutton(self.drawing_options_frame, text="Smooth SDF", 
                            variable=self.smoothing_var).grid(row=1, column=0, columnspan=2, sticky=tk.W)
                
                ttk.Button(self.drawing_options_frame, text="Clear Canvas", 
                        command=self.clear_drawing).grid(row=2, column=0, sticky=tk.W, pady=5)
                ttk.Button(self.drawing_options_frame, text="Apply", 
                        command=self.apply_drawing).grid(row=2, column=1, sticky=tk.E, pady=5)
            
            # Setup the drawing canvas
            self.setup_drawing_canvas()
            
        else:
            # Hide drawing options
            self.drawing_options_frame.grid_forget()
            
            # Remove drawing canvas bindings
            if hasattr(self, 'drawing_cid'):
                self.canvas.mpl_disconnect(self.drawing_cid_press)
                self.canvas.mpl_disconnect(self.drawing_cid_motion)
                self.canvas.mpl_disconnect(self.drawing_cid_release)
                delattr(self, 'drawing_cid_press')
                
            # Remove drawing overlay if it exists
            if hasattr(self, 'drawing_overlay') and self.drawing_overlay in self.ax_sdf.collections:
                self.drawing_overlay.remove()
    
    def setup_drawing_canvas(self):
        """Setup canvas for drawing shapes"""
        # Initialize drawing data
        self.drawing_mask = np.zeros((self.resolution, self.resolution), dtype=bool)
        self.drawing = False
        
        # Create a scatter plot for showing the drawn points
        self.drawing_overlay = self.ax_sdf.scatter([], [], s=1, color='white', alpha=0.7)
        
        # Connect event handlers
        self.drawing_cid_press = self.canvas.mpl_connect('button_press_event', self.on_drawing_press)
        self.drawing_cid_motion = self.canvas.mpl_connect('motion_notify_event', self.on_drawing_motion)
        self.drawing_cid_release = self.canvas.mpl_connect('button_release_event', self.on_drawing_release)
        
        # Show instructions
        self.ax_sdf.set_title("Drawing Mode: Click and drag to draw a shape", 
                            fontsize=12, color=FuturisticTheme.COLORS['accent'])
        self.canvas.draw()

    def on_drawing_press(self, event):
        """Handle mouse press for drawing"""
        if event.inaxes != self.ax_sdf:
            return
        
        self.drawing = True
        self.draw_at_position(event.xdata, event.ydata)

    def on_drawing_motion(self, event):
        """Handle mouse motion for drawing"""
        if not self.drawing or event.inaxes != self.ax_sdf:
            return
        
        self.draw_at_position(event.xdata, event.ydata)

    def on_drawing_release(self, event):
        """Handle mouse release for drawing"""
        self.drawing = False

    def draw_at_position(self, x, y):
        """Draw at the specified position in data coordinates"""
        if x is None or y is None:
            return
            
        # Convert data coordinates to pixel indices
        x_idx = int((x + self.domain_size) / (2 * self.domain_size) * (self.resolution - 1))
        y_idx = int((y + self.domain_size) / (2 * self.domain_size) * (self.resolution - 1))
        
        # Ensure indices are within bounds
        x_idx = max(0, min(x_idx, self.resolution - 1))
        y_idx = max(0, min(y_idx, self.resolution - 1))
        
        # Get brush size
        brush_size = self.brush_size_var.get()
        
        # Draw a circle at this position
        y_indices, x_indices = np.ogrid[-brush_size:brush_size+1, -brush_size:brush_size+1]
        mask = x_indices**2 + y_indices**2 <= brush_size**2
        
        # Apply the mask to the drawing
        for dy in range(-brush_size, brush_size+1):
            for dx in range(-brush_size, brush_size+1):
                if mask[dy+brush_size, dx+brush_size]:
                    ny, nx = y_idx + dy, x_idx + dx
                    if 0 <= ny < self.resolution and 0 <= nx < self.resolution:
                        self.drawing_mask[ny, nx] = True
        
        # Update the drawing overlay
        y_coords, x_coords = np.where(self.drawing_mask)
        
        # Convert indices back to data coordinates
        x_data = x_coords / (self.resolution - 1) * (2 * self.domain_size) - self.domain_size
        y_data = y_coords / (self.resolution - 1) * (2 * self.domain_size) - self.domain_size
        
        # Update the scatter plot
        self.drawing_overlay.set_offsets(np.column_stack([x_data, y_data]))
        self.canvas.draw_idle()

    def clear_drawing(self):
        """Clear the current drawing"""
        self.drawing_mask = np.zeros((self.resolution, self.resolution), dtype=bool)
        self.drawing_overlay.set_offsets(np.empty((0, 2)))
        self.canvas.draw_idle()

    def apply_drawing(self):
        """Apply the current drawing as a new shape"""
        if not np.any(self.drawing_mask):
            # Nothing drawn
            return
        
        # Compute SDF from the drawing mask
        sdf = self.compute_sdf_from_drawing()
        
        # Create a new shape based on the drawing
        shape = {
            'type': 'custom',
            'name': f"Custom Shape {len(self.shapes) + 1}",
            'sdf_data': sdf
        }
        
        # Add the shape
        self.shapes.append(shape)
        self.shapes_listbox.insert(tk.END, shape['name'])
        self.active_shape_index = len(self.shapes) - 1
        
        # Update display
        self.update_properties_panel()
        self.update_plot()
        
        # Clear the drawing for next use
        self.clear_drawing()
        
        # Exit drawing mode
        self.toggle_drawing_mode()

    def compute_sdf_from_drawing(self):
        """Compute a signed distance field from the drawing mask"""
        from scipy import ndimage
        
        # Create a copy of the drawing mask
        mask = self.drawing_mask.copy()
        
        # Determine inside/outside
        # We'll use a flood fill from the edges to determine the outside
        outside_mask = np.zeros_like(mask, dtype=bool)
        
        # Start with the border pixels
        border_mask = np.zeros_like(mask, dtype=bool)
        border_mask[0, :] = True
        border_mask[-1, :] = True
        border_mask[:, 0] = True
        border_mask[:, -1] = True
        
        # Find pixels that are on the border and not part of the drawing
        seeds = np.where(border_mask & ~mask)
        outside_mask[seeds] = True
        
        # Use binary dilation to flood fill until convergence
        old_count = 0
        while np.sum(outside_mask) != old_count:
            old_count = np.sum(outside_mask)
            outside_mask = ndimage.binary_dilation(outside_mask, 
                                                structure=np.ones((3, 3)), 
                                                mask=~mask)
        
        # The inside is everything that's not outside
        inside_mask = ~outside_mask
        
        # Compute distance from the boundary for both inside and outside
        outside_distance = ndimage.distance_transform_edt(~mask) / self.resolution * (2 * self.domain_size)
        inside_distance = ndimage.distance_transform_edt(mask) / self.resolution * (2 * self.domain_size)
        
        # Combine into a signed distance field
        sdf = np.zeros_like(outside_distance)
        sdf[outside_mask] = outside_distance[outside_mask]
        sdf[inside_mask] = -inside_distance[inside_mask]
        
        # Apply smoothing if requested
        if self.smoothing_var.get():
            sdf = ndimage.gaussian_filter(sdf, sigma=0.5)
        
        return sdf
    
    def update_grid(self):
        """Update the grid based on current resolution"""
        x = np.linspace(-self.domain_size, self.domain_size, self.resolution)
        y = np.linspace(-self.domain_size, self.domain_size, self.resolution)
        self.X, self.Y = np.meshgrid(x, y)

    def update_resolution(self, event=None):
        """"Update resolution from the entry field"""
        try:
            new_resolution = int(self.resolution_var.get())
            if new_resolution > 512:
                if not tk.messagebox.askyesno(
                    "High Resolution Warning",
                    "Setting resolution higher than 512 may cause performance issues. Continue?"
                ):
                    self.resolution_var.set(self.resolution)
                    return
            self.set_resolution(new_resolution)
        except ValueError:
            self.resolution_var.set(self.resolution)
    
    def set_resolution(self, new_resolution):
        """Set a new resolution and update visualization"""
        if new_resolution != self.resolution:
            self.resolution = new_resolution
            self.resolution_var.set(new_resolution)
            self.update_grid()
            self.update_plot()

    def create_button(self, parent, text, command, row):
        """Create a styled button"""
        btn = ttk.Button(parent, text=text, command=command)
        btn.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=2)
        return btn
    
    def toggle_unsigned_sdf(self):
        """Toggle between signed and unsigned distance field visualization"""
        self.use_unsigned_sdf = self.unsigned_var.get()
        self.update_plot()
    
    def update_boolean_op(self):
        self.boolean_operation = self.bool_var.get()
        self.update_plot()
    
    def update_visualization_style(self, event=None):
        self.visualization_style = self.viz_style_var.get()
        self.update_plot()
    
    def update_effect_strength(self, event=None):
        self.effect_strength = self.effect_var.get()
        self.update_plot()  # This should be called to refresh the visualization
    
    def toggle_animation(self):
        self.animation_active = self.anim_var.get()
        self.update_plot()
    
    def add_shape(self, shape_type):
        # Default shape parameters
        if shape_type == "circle":
            shape = {
                'type': 'circle',
                'name': f"Circle {len(self.shapes) + 1}",
                'position': [0.0, 0.0],
                'radius': 1.0
            }
        elif shape_type == "rectangle":
            shape = {
                'type': 'rectangle',
                'name': f"Rectangle {len(self.shapes) + 1}",
                'position': [0.0, 0.0],
                'dimensions': [2.0, 1.0],
                'rotation': 0.0
            }
        elif shape_type == "triangle":
            shape = {
                'type': 'triangle',
                'name': f"Triangle {len(self.shapes) + 1}",
                'vertices': [[-1.0, -1.0], [1.0, -1.0], [0.0, 1.0]]
            }
        elif shape_type == "line":
            shape = {
                'type': 'line',
                'name': f"Line {len(self.shapes) + 1}",
                'start': [-1.0, 0.0],
                'end': [1.0, 0.0],
                'thickness': 0.2
            }
        
        self.shapes.append(shape)
        self.shapes_listbox.insert(tk.END, shape['name'])
        self.active_shape_index = len(self.shapes) - 1
        self.update_properties_panel()
        self.update_plot()
    
    def remove_shape(self):
        if self.active_shape_index is not None:
            self.shapes.pop(self.active_shape_index)
            self.shapes_listbox.delete(self.active_shape_index)
            if len(self.shapes) > 0:
                self.active_shape_index = 0
                self.shapes_listbox.selection_set(0)
            else:
                self.active_shape_index = None
            self.update_properties_panel()
            self.update_plot()

    def save_visualization(self):
        """Save the current visualization as an image file"""
        try:
            # Use tkinter's file dialog to get save location
            from tkinter import filedialog, messagebox, simpledialog
            
            # Create a simple dialog to ask for save options
            class SaveOptionsDialog(simpledialog.Dialog):
                def body(self, master):
                    ttk.Label(master, text="Save Options:").grid(row=0, columnspan=2, sticky=tk.W, pady=(0, 10))
                    
                    self.include_axes = tk.BooleanVar(value=True)
                    ttk.Checkbutton(master, text="Include axes and labels", 
                                variable=self.include_axes).grid(row=1, columnspan=2, sticky=tk.W)
                    
                    self.include_title = tk.BooleanVar(value=True)
                    ttk.Checkbutton(master, text="Include title", 
                                variable=self.include_title).grid(row=2, columnspan=2, sticky=tk.W)
                    
                    self.include_grid = tk.BooleanVar(value=True)
                    ttk.Checkbutton(master, text="Include grid", 
                                variable=self.include_grid).grid(row=3, columnspan=2, sticky=tk.W)
                    
                    ttk.Label(master, text="DPI:").grid(row=4, column=0, sticky=tk.W, pady=(10, 0))
                    self.dpi_var = tk.IntVar(value=300)
                    ttk.Spinbox(master, from_=72, to=600, increment=1, 
                            textvariable=self.dpi_var, width=5).grid(row=4, column=1, sticky=tk.W, pady=(10, 0))
                    
                    return None  # No specific widget to get focus
                
                def apply(self):
                    self.result = {
                        'include_axes': self.include_axes.get(),
                        'include_title': self.include_title.get(),
                        'include_grid': self.include_grid.get(),
                        'dpi': self.dpi_var.get()
                    }
            
            # Show the options dialog
            dialog = SaveOptionsDialog(self.root, title="Save Options")
            if not dialog.result:  # User cancelled
                return
            
            options = dialog.result
            
            # Get file path
            file_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG Image", "*.png"), ("JPEG Image", "*.jpg"), ("SVG Image", "*.svg"), 
                        ("PDF Document", "*.pdf"), ("All Files", "*.*")],
                title="Save Visualization As"
            )
            
            if not file_path:  # User cancelled the dialog
                return
            
            # Instead of copying artists (which causes errors), we'll temporarily modify 
            # the visibility of elements in the current figure
            
            # Store original visibility settings to restore later
            original_settings = {
                'axis_visibility': self.ax_sdf.axison,
                'title_text': self.ax_sdf.get_title(),
                'xlabel_text': self.ax_sdf.get_xlabel(),
                'ylabel_text': self.ax_sdf.get_ylabel(),
                'grid_visibility': self.ax_sdf.grid(),
                'figure_facecolor': self.fig.get_facecolor(),
                'axes_facecolor': self.ax_sdf.get_facecolor()
            }
            
            # Temporarily modify the current figure based on options
            if not options['include_axes']:
                self.ax_sdf.set_axis_off()
                self.ax_sdf.set_xlabel('')
                self.ax_sdf.set_ylabel('')
                self.ax_sdf.tick_params(
                    axis='both', which='both', 
                    bottom=False, top=False, 
                    left=False, right=False,
                    labelbottom=False, labelleft=False
                )
            
            if not options['include_title']:
                self.ax_sdf.set_title('')
            
            if not options['include_grid']:
                self.ax_sdf.grid(False)
            
            # If we're saving without axes, make background transparent for a clean export
            if not options['include_axes']:
                self.fig.patch.set_alpha(0.0)
                self.ax_sdf.patch.set_alpha(0.0)
            
            # Save the current figure with the temporary modifications
            self.fig.savefig(
                file_path, 
                dpi=options['dpi'], 
                bbox_inches='tight',
                pad_inches=0 if not options['include_axes'] else 0.1,
                transparent=not options['include_axes']
            )
            
            # Restore original settings
            if not options['include_axes']:
                self.ax_sdf.set_axis_on()
                self.ax_sdf.tick_params(
                    axis='both', which='both', 
                    bottom=True, top=True, 
                    left=True, right=True,
                    labelbottom=True, labelleft=True
                )
                self.fig.patch.set_alpha(1.0)
                self.ax_sdf.patch.set_alpha(1.0)
            
            self.ax_sdf.set_title(original_settings['title_text'])
            self.ax_sdf.set_xlabel(original_settings['xlabel_text'])
            self.ax_sdf.set_ylabel(original_settings['ylabel_text'])
            self.ax_sdf.grid(original_settings['grid_visibility'])
            
            # Force a redraw to restore the visualization
            self.canvas.draw()
            
            # Show confirmation
            messagebox.showinfo("Success", f"Image saved to:\n{file_path}")
        
        except Exception as e:
            from tkinter import messagebox
            import traceback
            traceback.print_exc()  # Print full error details to console
            messagebox.showerror("Error", f"Failed to save image:\n{str(e)}")
    
    def clear_shapes(self):
        self.shapes = []
        self.shapes_listbox.delete(0, tk.END)
        self.active_shape_index = None
        self.update_properties_panel()
        self.update_plot()
    
    def on_shape_select(self, event):
        selection = self.shapes_listbox.curselection()
        if selection:
            self.active_shape_index = selection[0]
            self.update_properties_panel()
    
    def update_properties_panel(self):
        # Clear current properties widgets
        for widget in self.properties_frame.winfo_children():
            widget.destroy()
        
        if self.active_shape_index is None:
            ttk.Label(self.properties_frame, text="No shape selected").grid(row=0, column=0)
            return
        
        shape = self.shapes[self.active_shape_index]
        
        # Create appropriate controls based on shape type
        if shape['type'] == 'circle':
            # Position X
            ttk.Label(self.properties_frame, text="Position X:").grid(row=0, column=0, sticky=tk.W)
            pos_x_var = tk.DoubleVar(value=shape['position'][0])
            pos_x_entry = ttk.Entry(self.properties_frame, textvariable=pos_x_var, width=7)
            pos_x_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
            pos_x_entry.bind("<Return>", lambda e: self.update_shape_property('position', [pos_x_var.get(), shape['position'][1]]))
            
            # Position Y
            ttk.Label(self.properties_frame, text="Position Y:").grid(row=1, column=0, sticky=tk.W)
            pos_y_var = tk.DoubleVar(value=shape['position'][1])
            pos_y_entry = ttk.Entry(self.properties_frame, textvariable=pos_y_var, width=7)
            pos_y_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
            pos_y_entry.bind("<Return>", lambda e: self.update_shape_property('position', [shape['position'][0], pos_y_var.get()]))
            
            # Radius
            ttk.Label(self.properties_frame, text="Radius:").grid(row=2, column=0, sticky=tk.W)
            radius_var = tk.DoubleVar(value=shape['radius'])
            radius_entry = ttk.Entry(self.properties_frame, textvariable=radius_var, width=7)
            radius_entry.grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)
            radius_entry.bind("<Return>", lambda e: self.update_shape_property('radius', radius_var.get()))
            
        elif shape['type'] == 'rectangle':
            # Position X
            ttk.Label(self.properties_frame, text="Position X:").grid(row=0, column=0, sticky=tk.W)
            pos_x_var = tk.DoubleVar(value=shape['position'][0])
            pos_x_entry = ttk.Entry(self.properties_frame, textvariable=pos_x_var, width=7)
            pos_x_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
            pos_x_entry.bind("<Return>", lambda e: self.update_shape_property('position', [pos_x_var.get(), shape['position'][1]]))
            
            # Position Y
            ttk.Label(self.properties_frame, text="Position Y:").grid(row=1, column=0, sticky=tk.W)
            pos_y_var = tk.DoubleVar(value=shape['position'][1])
            pos_y_entry = ttk.Entry(self.properties_frame, textvariable=pos_y_var, width=7)
            pos_y_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
            pos_y_entry.bind("<Return>", lambda e: self.update_shape_property('position', [shape['position'][0], pos_y_var.get()]))
            
            # Width
            ttk.Label(self.properties_frame, text="Width:").grid(row=2, column=0, sticky=tk.W)
            width_var = tk.DoubleVar(value=shape['dimensions'][0])
            width_entry = ttk.Entry(self.properties_frame, textvariable=width_var, width=7)
            width_entry.grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)
            width_entry.bind("<Return>", lambda e: self.update_shape_property('dimensions', [width_var.get(), shape['dimensions'][1]]))
            
            # Height
            ttk.Label(self.properties_frame, text="Height:").grid(row=3, column=0, sticky=tk.W)
            height_var = tk.DoubleVar(value=shape['dimensions'][1])
            height_entry = ttk.Entry(self.properties_frame, textvariable=height_var, width=7)
            height_entry.grid(row=3, column=1, sticky=tk.W, padx=5, pady=2)
            height_entry.bind("<Return>", lambda e: self.update_shape_property('dimensions', [shape['dimensions'][0], height_var.get()]))
            
            # Rotation
            ttk.Label(self.properties_frame, text="Rotation:").grid(row=4, column=0, sticky=tk.W)
            rotation_var = tk.DoubleVar(value=shape['rotation'])
            rotation_entry = ttk.Entry(self.properties_frame, textvariable=rotation_var, width=7)
            rotation_entry.grid(row=4, column=1, sticky=tk.W, padx=5, pady=2)
            rotation_entry.bind("<Return>", lambda e: self.update_shape_property('rotation', rotation_var.get()))
            
        elif shape['type'] == 'line':
            # Start X
            ttk.Label(self.properties_frame, text="Start X:").grid(row=0, column=0, sticky=tk.W)
            start_x_var = tk.DoubleVar(value=shape['start'][0])
            start_x_entry = ttk.Entry(self.properties_frame, textvariable=start_x_var, width=7)
            start_x_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
            start_x_entry.bind("<Return>", lambda e: self.update_shape_property('start', [start_x_var.get(), shape['start'][1]]))
            
            # Start Y
            ttk.Label(self.properties_frame, text="Start Y:").grid(row=1, column=0, sticky=tk.W)
            start_y_var = tk.DoubleVar(value=shape['start'][1])
            start_y_entry = ttk.Entry(self.properties_frame, textvariable=start_y_var, width=7)
            start_y_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
            start_y_entry.bind("<Return>", lambda e: self.update_shape_property('start', [shape['start'][0], start_y_var.get()]))
            
            # End X
            ttk.Label(self.properties_frame, text="End X:").grid(row=2, column=0, sticky=tk.W)
            end_x_var = tk.DoubleVar(value=shape['end'][0])
            end_x_entry = ttk.Entry(self.properties_frame, textvariable=end_x_var, width=7)
            end_x_entry.grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)
            end_x_entry.bind("<Return>", lambda e: self.update_shape_property('end', [end_x_var.get(), shape['end'][1]]))
            
            # End Y
            ttk.Label(self.properties_frame, text="End Y:").grid(row=3, column=0, sticky=tk.W)
            end_y_var = tk.DoubleVar(value=shape['end'][1])
            end_y_entry = ttk.Entry(self.properties_frame, textvariable=end_y_var, width=7)
            end_y_entry.grid(row=3, column=1, sticky=tk.W, padx=5, pady=2)
            end_y_entry.bind("<Return>", lambda e: self.update_shape_property('end', [shape['end'][0], end_y_var.get()]))
            
            # Thickness
            ttk.Label(self.properties_frame, text="Thickness:").grid(row=4, column=0, sticky=tk.W)
            thickness_var = tk.DoubleVar(value=shape['thickness'])
            thickness_entry = ttk.Entry(self.properties_frame, textvariable=thickness_var, width=7)
            thickness_entry.grid(row=4, column=1, sticky=tk.W, padx=5, pady=2)
            thickness_entry.bind("<Return>", lambda e: self.update_shape_property('thickness', thickness_var.get()))

        elif shape['type'] == 'triangle':
            for i in range(3):
                # Vertex X
                ttk.Label(self.properties_frame, text=f"Vertex {i+1} X:").grid(row=i*2, column=0, sticky=tk.W)
                vertex_x_var = tk.DoubleVar(value=shape['vertices'][i][0])
                vertex_x_entry = ttk.Entry(self.properties_frame, textvariable=vertex_x_var, width=7)
                vertex_x_entry.grid(row=i*2, column=1, sticky=tk.W, padx=5, pady=2)
                vertex_x_entry.bind("<Return>", lambda e, i=i, var=vertex_x_var: self.update_triangle_vertex(i, [var.get(), shape['vertices'][i][1]]))
                
                # Vertex Y
                ttk.Label(self.properties_frame, text=f"Vertex {i+1} Y:").grid(row=i*2+1, column=0, sticky=tk.W)
                vertex_y_var = tk.DoubleVar(value=shape['vertices'][i][1])
                vertex_y_entry = ttk.Entry(self.properties_frame, textvariable=vertex_y_var, width=7)
                vertex_y_entry.grid(row=i*2+1, column=1, sticky=tk.W, padx=5, pady=2)
                vertex_y_entry.bind("<Return>", lambda e, i=i, var=vertex_y_var: self.update_triangle_vertex(i, [shape['vertices'][i][0], var.get()]))
    
    def update_shape_property(self, property_name, value):
        if self.active_shape_index is not None:
            self.shapes[self.active_shape_index][property_name] = value
            self.update_plot()
    
    def update_triangle_vertex(self, vertex_index, value):
        if self.active_shape_index is not None:
            self.shapes[self.active_shape_index]['vertices'][vertex_index] = value
            self.update_plot()

    def compute_sdf(self, shape, x, y):
        # Compute the SDF for a single shape
        if shape['type'] == 'circle':
            px, py = shape['position']
            r = shape['radius']
            return np.sqrt((x - px)**2 + (y - py)**2) - r
            
        elif shape['type'] == 'rectangle':
            px, py = shape['position']
            width, height = shape['dimensions']
            rotation = shape['rotation'] * np.pi / 180  # Convert to radians
            
            # Rotate the point
            s, c = np.sin(-rotation), np.cos(-rotation)
            dx, dy = x - px, y - py
            rx, ry = c * dx - s * dy, s * dx + c * dy
            
            # Box SDF
            box_x = np.abs(rx) - width/2
            box_y = np.abs(ry) - height/2
            outside = np.sqrt(np.maximum(box_x, 0)**2 + np.maximum(box_y, 0)**2)
            inside = np.minimum(np.maximum(box_x, box_y), 0)
            return outside + inside
            
        elif shape['type'] == 'line':
            p1x, p1y = shape['start']
            p2x, p2y = shape['end']
            t = shape['thickness'] / 2
            
            # Line segment SDF
            px, py = x, y
            ax, ay = p1x, p1y
            bx, by = p2x, p2y
            
            # Calculate vector from a to b
            abx, aby = bx - ax, by - ay
            
            # Calculate squared length of ab
            ab_squared = abx**2 + aby**2
            
            # If the line segment has zero length, treat it as a point
            if ab_squared < 1e-10:
                return np.sqrt((px - ax)**2 + (py - ay)**2) - t
            
            # Calculate projection of p onto ab
            apx, apy = px - ax, py - ay
            projection = (apx * abx + apy * aby) / ab_squared
            
            # Clamp the projection to [0, 1] for line segment
            projection = np.clip(projection, 0, 1)
            
            # Calculate the closest point on the line segment
            closest_x = ax + projection * abx
            closest_y = ay + projection * aby
            
            # Calculate the distance from p to the closest point
            distance = np.sqrt((px - closest_x)**2 + (py - closest_y)**2)
            
            return distance - t
            
        elif shape['type'] == 'triangle':
            vertices = shape['vertices']
            v1x, v1y = vertices[0]
            v2x, v2y = vertices[1]
            v3x, v3y = vertices[2]
            
            # Triangle SDF
            px, py = x, y
            
            # Calculate distance to each edge
            # Edge 1: v1 to v2
            edge1_distance = self._distance_to_line_segment(px, py, v1x, v1y, v2x, v2y)
            
            # Edge 2: v2 to v3
            edge2_distance = self._distance_to_line_segment(px, py, v2x, v2y, v3x, v3y)
            
            # Edge 3: v3 to v1
            edge3_distance = self._distance_to_line_segment(px, py, v3x, v3y, v1x, v1y)
            
            # Minimum distance to any edge
            distance = np.minimum(np.minimum(edge1_distance, edge2_distance), edge3_distance)
            
            # Check if point is inside triangle
            # For a point inside the triangle, all cross products should have the same sign
            a1 = (v1y - py) * (v2x - v1x) - (v1x - px) * (v2y - v1y)
            a2 = (v2y - py) * (v3x - v2x) - (v2x - px) * (v3y - v2y)
            a3 = (v3y - py) * (v1x - v3x) - (v3x - px) * (v1y - v3y)
            
            # If all have the same sign, point is inside
            inside = ((a1 >= 0) & (a2 >= 0) & (a3 >= 0)) | ((a1 <= 0) & (a2 <= 0) & (a3 <= 0))
            
            return np.where(inside, -distance, distance)

        elif shape['type'] == 'custom':
            # For custom shapes, we already have the SDF data
            # We need to interpolate it to match the current resolution
            from scipy.interpolate import RegularGridInterpolator
            
            custom_sdf = shape['sdf_data']
            h, w = custom_sdf.shape
            
            # Create coordinate grids for the original data
            x_orig = np.linspace(-self.domain_size, self.domain_size, w)
            y_orig = np.linspace(-self.domain_size, self.domain_size, h)
            
            # Create interpolator
            interpolator = RegularGridInterpolator((y_orig, x_orig), custom_sdf,
                                                bounds_error=False, fill_value=self.domain_size)
            
            # Create points to query
            points = np.column_stack([y.flatten(), x.flatten()])
            
            # Compute interpolated SDF values
            interp_sdf = interpolator(points).reshape(x.shape)
            
            return interp_sdf
        
        # Default fallback
        return np.inf * np.ones_like(x)
    
    def _distance_to_line_segment(self, px, py, x1, y1, x2, y2):
        """Calculate the distance from a point (px, py) to a line segment (x1,y1)-(x2,y2)"""
        # Line segment vector
        vx, vy = x2 - x1, y2 - y1
        
        # Calculate squared length of segment
        segment_length_squared = vx**2 + vy**2
        
        # Handle degenerate line segment
        if segment_length_squared < 1e-10:
            return np.sqrt((px - x1)**2 + (py - y1)**2)
        
        # Project point onto line segment
        t = np.clip(((px - x1) * vx + (py - y1) * vy) / segment_length_squared, 0, 1)
        
        # Closest point on line segment
        closest_x = x1 + t * vx
        closest_y = y1 + t * vy
        
        # Distance to closest point
        return np.sqrt((px - closest_x)**2 + (py - closest_y)**2)
    
    def combine_sdfs(self, sdf1, sdf2, operation):
        # Combine two SDFs based on the operation
        if operation == "union":
            return np.minimum(sdf1, sdf2)
        elif operation == "intersection":
            return np.maximum(sdf1, sdf2)
        elif operation == "difference":
            return np.maximum(sdf1, -sdf2)
        elif operation == "smooth_union":
            k = 0.25  # Smoothing factor
            h = np.clip(0.5 + 0.5 * (sdf2 - sdf1) / k, 0.0, 1.0)
            return np.mix(sdf2, sdf1, h) - k * h * (1.0 - h)
        else:  # "none" or default
            return sdf1
    
    def update_plot(self):
        # Stop any existing animation
        if self.animation is not None:
            self.animation.event_source.stop()
            self.animation = None
        
        # Compute the combined SDF
        sdf = None
        
        for i, shape in enumerate(self.shapes):
            shape_sdf = self.compute_sdf(shape, self.X, self.Y)
            
            if sdf is None:
                sdf = shape_sdf
            elif self.boolean_operation == "none":
                sdf = np.minimum(sdf, shape_sdf)  # Default to union if no operation selected
            else:
                sdf = self.combine_sdfs(sdf, shape_sdf, self.boolean_operation)
        
        # If no shapes, set a default SDF
        if sdf is None:
            sdf = np.ones_like(self.X) * self.domain_size
        
        # Apply unsigned transformation if enabled
        display_sdf = np.abs(sdf) if self.use_unsigned_sdf else sdf
        
        # Clear previous plots
        self.ax_sdf.clear()
        
        # Store the SDF data for coordinate display
        self.ax_sdf.sdf_data = sdf  # Store original SDF for accurate distance values
        self.ax_sdf.sdf_extent = [-self.domain_size, self.domain_size, -self.domain_size, self.domain_size]
        
        # Add futuristic grid lines
        FuturisticTheme.add_grid_lines(self.ax_sdf, spacing=1.0)
        
        # Apply visualization based on selected style
        if self.visualization_style == "Standard":
            # Choose colormap based on signed/unsigned
            if self.use_unsigned_sdf:
                # For unsigned, use a single-direction colormap (white to red)
                cmap = LinearSegmentedColormap.from_list(
                    "unsigned_sdf", [(1, 1, 1), (1, 0, 0)], N=100)
                vmin, vmax = 0, self.domain_size/2
            else:
                # For signed, use the standard blue-white-red colormap
                cmap = FuturisticTheme.get_colormap()
                vmin, vmax = -self.domain_size/2, self.domain_size/2
            
            # Plot the SDF
            contour = self.ax_sdf.contourf(self.X, self.Y, display_sdf, levels=50, 
                                        cmap=cmap, extend='both', vmin=vmin, vmax=vmax)
            
            # Add contour lines for the zero level (shape boundaries)
            # For unsigned SDF, show contour at the original zero crossing
            self.ax_sdf.contour(self.X, self.Y, sdf, levels=[0], colors='white', linewidths=2)
            
        elif self.visualization_style == "Hologram":
            # Holographic effect
            holo_image = AdvancedVisualization.create_holographic_effect(sdf, self.domain_size)
            self.ax_sdf.imshow(holo_image, extent=[-self.domain_size, self.domain_size, -self.domain_size, self.domain_size], 
                             origin='lower')
            
        elif self.visualization_style == "Neon":
            # Neon wireframe effect
            neon_image = AdvancedVisualization.create_neon_wireframe(sdf, self.domain_size)
            self.ax_sdf.imshow(neon_image, extent=[-self.domain_size, self.domain_size, -self.domain_size, self.domain_size], 
                             origin='lower')
            
        elif self.visualization_style == "Heatmap":
            # Heatmap visualization
            heatmap = AdvancedVisualization.create_heatmap_visualization(sdf, self.domain_size)
            self.ax_sdf.imshow(heatmap, extent=[-self.domain_size, self.domain_size, -self.domain_size, self.domain_size], 
                             origin='lower')
            
        elif self.visualization_style == "Electric":
            # Electric field visualization
            electric = AdvancedVisualization.create_electric_field_visualization(sdf, self.domain_size)
            self.ax_sdf.imshow(electric, extent=[-self.domain_size, self.domain_size, -self.domain_size, self.domain_size], 
                             origin='lower')
        
        # Set axis labels and limits
        self.ax_sdf.set_xlabel('X', fontsize=10, color=FuturisticTheme.COLORS['text'])
        self.ax_sdf.set_ylabel('Y', fontsize=10, color=FuturisticTheme.COLORS['text'])
        self.ax_sdf.set_xlim(-self.domain_size, self.domain_size)
        self.ax_sdf.set_ylim(-self.domain_size, self.domain_size)
        
        # Set title based on signed/unsigned choice
        title = 'Unsigned Distance Field' if self.use_unsigned_sdf else 'Signed Distance Field'
        self.ax_sdf.set_title(title, fontsize=12, color=FuturisticTheme.COLORS['accent'])
        
        # If animation is active, start the animation
        if self.animation_active and sdf is not None:
            self.animation = AdvancedVisualization.create_animated_pulse_effect(
                self.ax_sdf, sdf, self.domain_size, frames=60, interval=50)
        
        # Adjust layout and redraw
        self.fig.tight_layout()
        self.canvas.draw()

# Helper functions
def np_mix(x, y, a):
    """Numpy implementation of GLSL's mix function (linear interpolation)"""
    return x * (1 - a) + y * a

# Add the mix function to numpy's namespace for the smooth union operation
np.mix = np_mix

def main():
    # Create Tkinter root window
    root = tk.Tk()
    app = FuturisticSDFVisualizer(root)
    root.geometry("1280x800")
    root.configure(bg=FuturisticTheme.COLORS['bg_dark'])
    
    # Set window icon and title
    root.title("Futuristic SDF Visualizer")
    
    # Start the application
    root.mainloop()

if __name__ == "__main__":
    main()