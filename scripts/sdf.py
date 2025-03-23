import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.gridspec as gridspec
from matplotlib.widgets import Slider, Button, RadioButtons
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.cm as cm

class SDF2DVisualizer:
    def __init__(self, root, resolution=200, domain_size=5.0):
        self.root = root
        self.root.title("2D SDF Visualizer")
        self.resolution = resolution
        self.domain_size = domain_size
        
        # Create a grid of x,y coordinates
        x = np.linspace(-domain_size, domain_size, resolution)
        y = np.linspace(-domain_size, domain_size, resolution)
        self.X, self.Y = np.meshgrid(x, y)
        
        # Initialize with some default shapes
        self.shapes = []
        self.active_shape_index = None
        self.boolean_operation = None
        
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
        left_panel = ttk.Frame(main_frame, padding=5, relief="raised", borderwidth=1)
        left_panel.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        # Create right panel for visualization
        right_panel = ttk.Frame(main_frame, padding=5)
        right_panel.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        # Configure weights
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=3)
        main_frame.rowconfigure(0, weight=1)
        
        # Create shape selection section
        shape_frame = ttk.LabelFrame(left_panel, text="Add Shape", padding=5)
        shape_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Shape buttons
        ttk.Button(shape_frame, text="Circle", command=lambda: self.add_shape("circle")).grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Button(shape_frame, text="Rectangle", command=lambda: self.add_shape("rectangle")).grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Button(shape_frame, text="Triangle", command=lambda: self.add_shape("triangle")).grid(row=2, column=0, sticky=tk.W, pady=2)
        ttk.Button(shape_frame, text="Line", command=lambda: self.add_shape("line")).grid(row=3, column=0, sticky=tk.W, pady=2)
        
        # Boolean operations section
        bool_frame = ttk.LabelFrame(left_panel, text="Boolean Operation", padding=5)
        bool_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
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
        
        # Shape properties section
        self.properties_frame = ttk.LabelFrame(left_panel, text="Shape Properties", padding=5)
        self.properties_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Shape list section
        shapes_frame = ttk.LabelFrame(left_panel, text="Shapes", padding=5)
        shapes_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Listbox for shapes
        self.shapes_listbox = tk.Listbox(shapes_frame, height=5)
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
        left_panel.rowconfigure(3, weight=1)
        left_panel.columnconfigure(0, weight=1)
        
        # Create the matplotlib figure for visualization
        self.fig = Figure(figsize=(8, 8), dpi=100)
        gs = gridspec.GridSpec(2, 1, height_ratios=[4, 1])
        
        # SDF visualization
        self.ax_sdf = self.fig.add_subplot(gs[0])
        self.ax_sdf.set_title("SDF Visualization")
        self.ax_sdf.set_aspect('equal')
        
        # Color bar for the SDF values
        self.ax_colorbar = self.fig.add_subplot(gs[1])
        self.ax_colorbar.set_title("Distance Values")
        
        # Embed the matplotlib figure in tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=right_panel)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Add toolbar
        toolbar_frame = ttk.Frame(right_panel)
        toolbar_frame.pack(fill=tk.X)
        toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
        toolbar.update()
        
        # Initialize the plot
        self.update_plot()
    
    def update_boolean_op(self):
        self.boolean_operation = self.bool_var.get()
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
            
            # Edge vectors
            e1x, e1y = v2x - v1x, v2y - v1y
            e2x, e2y = v3x - v2x, v3y - v2y
            e3x, e3y = v1x - v3x, v1y - v3y
            
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
        
        # Default fallback
        return np.inf * np.ones_like(x)
    
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
        
        # Clear previous plots
        self.ax_sdf.clear()
        self.ax_colorbar.clear()
        
        # Create a custom colormap
        # Transition from blue (negative, inside) to white (zero, boundary) to red (positive, outside)
        colors = [(0, 0, 1), (1, 1, 1), (1, 0, 0)]  # Blue -> White -> Red
        n_bins = 100
        cmap = LinearSegmentedColormap.from_list("sdf_cmap", colors, N=n_bins)
        
        # Clip SDF values for better visualization
        vmin, vmax = -self.domain_size/2, self.domain_size/2
        clipped_sdf = np.clip(sdf, vmin, vmax)
        
        # Plot the SDF as a colored contour
        contour = self.ax_sdf.contourf(self.X, self.Y, clipped_sdf, levels=50, cmap=cmap, extend='both')
        
        # Add contour lines for the zero level (shape boundaries)
        self.ax_sdf.contour(self.X, self.Y, sdf, levels=[0], colors='black', linewidths=2)
        
        # Add more contour lines for better visualization
        self.ax_sdf.contour(self.X, self.Y, sdf, levels=10, colors='black', linewidths=0.5, alpha=0.5)
        
        # Set axis labels and limits
        self.ax_sdf.set_xlabel('X')
        self.ax_sdf.set_ylabel('Y')
        self.ax_sdf.set_xlim(-self.domain_size, self.domain_size)
        self.ax_sdf.set_ylim(-self.domain_size, self.domain_size)
        self.ax_sdf.set_title('SDF Visualization', fontsize=12)
        self.ax_sdf.grid(True, linestyle='--', alpha=0.3)
        
        # Create a horizontal colorbar
        cbar = plt.colorbar(contour, cax=self.ax_colorbar, orientation='horizontal')
        cbar.set_label('Signed Distance')
        
        # Add zero marker on the colorbar
        if vmin <= 0 <= vmax:
            zero_pos = (0 - vmin) / (vmax - vmin)
            self.ax_colorbar.axvline(zero_pos, color='black', linestyle='-', linewidth=2)
            self.ax_colorbar.text(zero_pos, 0.5, '0', transform=self.ax_colorbar.transAxes, 
                                 ha='center', va='center', color='black', fontweight='bold')
        
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
    root = tk.Tk()
    app = SDF2DVisualizer(root)
    root.geometry("1200x800")
    root.mainloop()

if __name__ == "__main__":
    main()