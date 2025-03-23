import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.gridspec as gridspec
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Slider, RadioButtons
import scipy.ndimage as ndimage

class AdvancedVisualization:
    """Advanced visualization effects for the SDF visualizer"""
    
    @staticmethod
    def create_holographic_effect(sdf, domain_size=5.0, resolution=200, glow_intensity=1.0, scanline_intensity=0.5):
        """Create a holographic effect for the SDF visualization with adjustable intensity"""
        # Create a grid
        x = np.linspace(-domain_size, domain_size, resolution)
        y = np.linspace(-domain_size, domain_size, resolution)
        X, Y = np.meshgrid(x, y)
        
        # Create a holographic effect with scanlines and noise
        scanlines = np.sin(Y * 50) * scanline_intensity * 0.1 + 0.95
        noise = np.random.normal(0, 0.03 * scanline_intensity, sdf.shape)
        
        # Apply distance-based highlighting
        distance_highlight = np.exp(-np.abs(sdf) * 3)
        
        # Create an RGB image
        rgb_image = np.zeros((resolution, resolution, 4))  # RGBA
        
        # Base color is cyan for hologram
        rgb_image[..., 0] = 0.0  # R
        rgb_image[..., 1] = 0.8  # G
        rgb_image[..., 2] = 1.0  # B
        
        # Fade based on distance and apply scanlines
        fade = distance_highlight * scanlines + noise
        rgb_image[..., 0] *= fade
        rgb_image[..., 1] *= fade
        rgb_image[..., 2] *= fade
        
        # Alpha channel - more opaque near the boundary
        rgb_image[..., 3] = distance_highlight * 0.8 + 0.2
        
        # Add a glow for the boundary - intensity affected by glow_intensity
        boundary_mask = np.abs(sdf) < 0.1
        # Adjust sigma based on glow intensity for wider or narrower glow
        glow = ndimage.gaussian_filter(boundary_mask.astype(float), sigma=2 + glow_intensity * 3)
        
        # Enhance the glow based on intensity
        rgb_image[..., 0] += glow * 0.2 * glow_intensity
        rgb_image[..., 1] += glow * 0.8 * glow_intensity
        rgb_image[..., 2] += glow * 1.0 * glow_intensity
        rgb_image[..., 3] = np.maximum(rgb_image[..., 3], glow * 0.7 * glow_intensity)
        
        # Clip values to valid range
        rgb_image = np.clip(rgb_image, 0, 1)
        
        return rgb_image

    @staticmethod
    def create_neon_wireframe(sdf, domain_size=5.0, resolution=200, glow_intensity=1.0, edge_thickness=1.0):
        """Create a neon wireframe visualization with adjustable intensity"""
        # Create a grid
        x = np.linspace(-domain_size, domain_size, resolution)
        y = np.linspace(-domain_size, domain_size, resolution)
        X, Y = np.meshgrid(x, y)
        
        # Calculate the gradient for edge detection
        gradient_y, gradient_x = np.gradient(sdf)
        gradient_magnitude = np.sqrt(gradient_x**2 + gradient_y**2)
        
        # Find edges - places where the gradient magnitude is high
        # Edge thickness affected by edge_thickness parameter
        threshold = 0.2 / edge_thickness  # Smaller threshold = thicker edges
        edges = np.abs(gradient_magnitude - 1.0) < threshold
        
        # Add contour lines for the zero level - thickness affected by edge_thickness
        boundary = np.abs(sdf) < (0.05 * edge_thickness)
        
        # Create distance-based highlighting
        distance_highlight = np.exp(-np.abs(sdf) * 5)
        
        # Combine edges and boundary
        wireframe = np.maximum(edges * 0.5, boundary)
        
        # Add glow - intensity affected by glow_intensity
        # Adjust sigma based on glow_intensity - larger sigma = wider glow
        sigma = 0.5 + glow_intensity * 1.5
        glow = ndimage.gaussian_filter(wireframe, sigma=sigma)
        
        # Create an RGB image with neon colors
        rgb_image = np.zeros((resolution, resolution, 4))  # RGBA
        
        # Inside: Cyan/Blue glow - intensity affected by glow_intensity
        rgb_image[..., 0] = 0.0  # R
        rgb_image[..., 1] = glow * (sdf < 0) * 0.8 * glow_intensity  # G
        rgb_image[..., 2] = glow * (sdf < 0) * 1.0 * glow_intensity  # B
        
        # Outside: Pink/Purple glow - intensity affected by glow_intensity
        rgb_image[..., 0] += glow * (sdf >= 0) * 1.0 * glow_intensity  # R
        rgb_image[..., 1] += glow * (sdf >= 0) * 0.2 * glow_intensity  # G
        rgb_image[..., 2] += glow * (sdf >= 0) * 0.8 * glow_intensity  # B
        
        # Boundaries: White - more pronounced with higher edge_thickness
        boundary_intensity = 1.0 * edge_thickness
        rgb_image[..., 0] += boundary * boundary_intensity  # R
        rgb_image[..., 1] += boundary * boundary_intensity  # G
        rgb_image[..., 2] += boundary * boundary_intensity  # B
        
        # Alpha channel - more opaque with higher glow_intensity
        rgb_image[..., 3] = np.maximum(glow * 0.7 * glow_intensity, boundary * 0.9 * edge_thickness)
        
        # Add background grid for better orientation
        grid_x = (np.abs(X * 5) % 1 < 0.02) * 0.15
        grid_y = (np.abs(Y * 5) % 1 < 0.02) * 0.15
        grid = np.maximum(grid_x, grid_y)
        
        # Apply grid where alpha is low
        low_alpha = rgb_image[..., 3] < 0.3
        rgb_image[low_alpha, 0] = 0.1
        rgb_image[low_alpha, 1] = 0.1
        rgb_image[low_alpha, 2] = 0.2
        rgb_image[low_alpha, 3] = 0.5
        
        # Add grid
        rgb_image[..., 0] += grid * 0.2
        rgb_image[..., 1] += grid * 0.2
        rgb_image[..., 2] += grid * 0.3
        rgb_image[..., 3] = np.maximum(rgb_image[..., 3], grid * 0.6)
        
        # Clip values to valid range
        rgb_image = np.clip(rgb_image, 0, 1)
        
        return rgb_image

    @staticmethod
    def create_heatmap_visualization(sdf, domain_size=5.0, resolution=200, contrast=1.0, contour_intensity=0.5):
        """Create a thermal/heatmap visualization with adjustable contrast and contour intensity"""
        # Create a grid
        x = np.linspace(-domain_size, domain_size, resolution)
        y = np.linspace(-domain_size, domain_size, resolution)
        X, Y = np.meshgrid(x, y)
        
        # Calculate normalized SDF values for the heatmap
        # Map from typical SDF range to 0-1 range
        # Adjust contrast with the contrast parameter
        normalized = np.clip((sdf + domain_size/2) / domain_size, 0, 1)
        
        # Apply contrast adjustment
        normalized = 0.5 + (normalized - 0.5) * contrast
        normalized = np.clip(normalized, 0, 1)
        
        # Create a heatmap colormap
        colors = [
            (0, 0, 0.5),     # Dark blue
            (0, 0, 1),       # Blue
            (0, 0.5, 1),     # Light blue
            (0, 1, 1),       # Cyan
            (0, 1, 0.5),     # Teal
            (0, 1, 0),       # Green
            (0.5, 1, 0),     # Lime
            (1, 1, 0),       # Yellow
            (1, 0.5, 0),     # Orange
            (1, 0, 0),       # Red
            (0.5, 0, 0)      # Dark red
        ]
        heatmap_cmap = LinearSegmentedColormap.from_list("thermal", colors, N=256)
        
        # Apply the colormap to get RGB values
        heatmap = heatmap_cmap(normalized)
        
        # Enhance the boundary - more pronounced with higher contour_intensity
        boundary = np.exp(-np.abs(sdf) * (10 + 20 * contour_intensity))
        boundary_intensity = 0.5 + 0.5 * contour_intensity
        heatmap[..., 0] += boundary * boundary_intensity * 1.0
        heatmap[..., 1] += boundary * boundary_intensity * 1.0
        heatmap[..., 2] += boundary * boundary_intensity * 1.0
        heatmap[..., 3] = 1.0
        
        # Add contour lines with intensity affected by contour_intensity
        # More contour lines with higher intensity
        num_contours = int(10 + 20 * contour_intensity)
        contours = np.zeros_like(sdf, dtype=bool)
        
        for level in np.linspace(-domain_size/2, domain_size/2, num_contours):
            # Contour thickness affected by contour_intensity
            threshold = 0.05 + 0.05 * contour_intensity
            contours = np.logical_or(contours, np.abs(sdf - level) < threshold)
        
        # Apply contours - more pronounced with higher contour_intensity
        contour_intensity_scaled = 0.3 + 0.7 * contour_intensity
        contour_mask = ndimage.gaussian_filter(contours.astype(float), sigma=0.5) > 0.1
        heatmap[contour_mask, 0] *= (1.0 - 0.7 * contour_intensity_scaled)
        heatmap[contour_mask, 1] *= (1.0 - 0.7 * contour_intensity_scaled)
        heatmap[contour_mask, 2] *= (1.0 - 0.7 * contour_intensity_scaled)
        
        # Clip values to valid range
        heatmap = np.clip(heatmap, 0, 1)
        
        return heatmap

    @staticmethod
    def create_electric_field_visualization(sdf, domain_size=5.0, resolution=200, field_intensity=1.0, glow_strength=1.0):
        """Create an electric field visualization using the SDF gradient with adjustable intensity"""
        # Create a grid
        x = np.linspace(-domain_size, domain_size, resolution)
        y = np.linspace(-domain_size, domain_size, resolution)
        X, Y = np.meshgrid(x, y)
        
        # Calculate the gradient (normalized)
        gradient_y, gradient_x = np.gradient(sdf)
        gradient_magnitude = np.sqrt(gradient_x**2 + gradient_y**2)
        
        # Avoid division by zero
        mask = gradient_magnitude > 1e-10
        gradient_x[mask] /= gradient_magnitude[mask]
        gradient_y[mask] /= gradient_magnitude[mask]
        
        # Create an RGB image
        rgb_image = np.zeros((resolution, resolution, 4))  # RGBA
        
        # Map gradient direction to color
        # This creates a cyclic color map based on angle
        angle = np.arctan2(gradient_y, gradient_x)
        
        # Normalize angle to 0-1 range
        angle_normalized = (angle + np.pi) / (2 * np.pi)
        
        # Create a cyclic color map for direction
        colors = [
            (1, 0, 0),      # Red
            (1, 1, 0),      # Yellow
            (0, 1, 0),      # Green
            (0, 1, 1),      # Cyan
            (0, 0, 1),      # Blue
            (1, 0, 1),      # Magenta
            (1, 0, 0)       # Red again to complete the cycle
        ]
        direction_cmap = LinearSegmentedColormap.from_list("direction", colors, N=256)
        
        # Apply the colormap to get direction-based RGB values
        direction_rgb = direction_cmap(angle_normalized)
        
        # Modify intensity based on distance to the boundary
        # More pronounced with higher field_intensity
        intensity = np.exp(-np.abs(sdf) * (1 + field_intensity))
        
        # Create "electric field lines" effect
        # We'll use a sine pattern based on the distance along the gradient direction
        # Frequency affected by field_intensity - higher = more lines
        frequency = 5 + 10 * field_intensity
        phase = (X * gradient_x + Y * gradient_y) * frequency
        lines = 0.7 + 0.3 * np.sin(phase)**2
        
        # Apply the electric field effect - intensity affected by field_intensity
        field_scaling = 0.5 + 0.5 * field_intensity
        rgb_image[..., 0] = direction_rgb[..., 0] * intensity * lines * field_scaling
        rgb_image[..., 1] = direction_rgb[..., 1] * intensity * lines * field_scaling
        rgb_image[..., 2] = direction_rgb[..., 2] * intensity * lines * field_scaling
        
        # Add a glow at the boundary - intensity affected by glow_strength
        boundary = np.exp(-np.abs(sdf) * (5 + 10 * glow_strength))
        
        # Adjust sigma based on glow_strength - wider glow with higher value
        sigma = 1 + 2 * glow_strength
        glow = ndimage.gaussian_filter(boundary, sigma=sigma)
        
        # Apply glow with intensity affected by glow_strength
        glow_scaling = 0.5 + 1.5 * glow_strength
        rgb_image[..., 0] += glow * 1.0 * glow_scaling
        rgb_image[..., 1] += glow * 1.0 * glow_scaling
        rgb_image[..., 2] += glow * 1.0 * glow_scaling
        
        # Alpha channel - affected by both field_intensity and glow_strength
        alpha_scaling = 0.7 + 0.3 * (field_intensity + glow_strength) / 2
        rgb_image[..., 3] = np.maximum(intensity * 0.8 * field_intensity, 
                                    glow * 0.9 * glow_strength) * alpha_scaling
        
        # Clip values to valid range
        rgb_image = np.clip(rgb_image, 0, 1)
        
        return rgb_image
    
    @staticmethod
    def create_animated_pulse_effect(ax, sdf, domain_size=5.0, frames=60, interval=50):
        """Create an animated pulsating effect for the SDF"""
        # Store the SDF for later access
        ax.sdf_data = sdf
        ax.sdf_extent = [-domain_size, domain_size, -domain_size, domain_size]
        
        # Initial plot
        im = ax.imshow(
            np.zeros_like(sdf), 
            extent=ax.sdf_extent,
            cmap='viridis',
            origin='lower'
        )
        
        # Initial contour - stored for later reference
        contour = ax.contour(
            sdf, 
            levels=[0], 
            colors=['white'], 
            linewidths=2,
            extent=ax.sdf_extent
        )
        
        # Store artists and collections for safe removal
        artists = {'contour': contour, 'glow_contours': []}
        
        def update(frame):
            # Pulse frequency
            t = frame / frames
            pulse = np.sin(t * 2 * np.pi) * 0.5 + 0.5
            
            # Calculate distance-based effect with pulsating radius
            pulse_radius = 0.5 + 2.0 * pulse
            distance_effect = np.exp(-np.abs(sdf) / pulse_radius)
            
            # Apply color based on inside/outside
            colored_effect = np.zeros((sdf.shape[0], sdf.shape[1], 4))
            
            # Inside: Blue with pulsating intensity
            inside = sdf < 0
            colored_effect[inside, 0] = 0.2 * pulse  # R
            colored_effect[inside, 1] = 0.5 * pulse  # G
            colored_effect[inside, 2] = 1.0 * pulse  # B
            colored_effect[inside, 3] = distance_effect[inside] * 0.8
            
            # Outside: Red with pulsating intensity
            outside = ~inside
            colored_effect[outside, 0] = 1.0 * pulse  # R
            colored_effect[outside, 1] = 0.5 * pulse  # G
            colored_effect[outside, 2] = 0.2 * pulse  # B
            colored_effect[outside, 3] = distance_effect[outside] * 0.8
            
            # Update image
            im.set_array(colored_effect)
            
            # Safely remove previous contours
            if 'contour' in artists and artists['contour'] is not None:
                for coll in artists['contour'].collections:
                    if coll in ax.collections:
                        coll.remove()
                
            # Also remove any glow contours
            if 'glow_contours' in artists:
                for glow_contour in artists['glow_contours']:
                    for coll in glow_contour.collections:
                        if coll in ax.collections:
                            coll.remove()
                            
            artists['glow_contours'] = []
            
            # Pulsating contour width
            width = 1.5 + pulse * 2
            
            # Create new contour with updated style
            contour_new = ax.contour(
                sdf, 
                levels=[0], 
                colors=['white'], 
                linewidths=width,
                extent=ax.sdf_extent
            )
            
            # Store the new contour for later removal
            artists['contour'] = contour_new
            
            # Add glow effect
            glow_colors = [(1, 1, 1, a) for a in [0.7, 0.5, 0.3, 0.1]]
            glow_widths = [width * (1 + i*0.5) for i in range(4)]
            
            glow_contours = []
            for i in range(4):
                glow_contour = ax.contour(
                    sdf, 
                    levels=[0], 
                    colors=[glow_colors[i]], 
                    linewidths=glow_widths[i],
                    extent=ax.sdf_extent
                )
                glow_contours.append(glow_contour)
            
            # Store glow contours for later removal
            artists['glow_contours'] = glow_contours
            
            # Collect all the artists that need to be updated
            all_artists = [im]
            all_artists.extend([c for c in contour_new.collections])
            for gc in glow_contours:
                all_artists.extend([c for c in gc.collections])
                
            return all_artists
        
        ani = FuncAnimation(
            ax.figure, 
            update, 
            frames=frames,
            interval=interval,
            blit=True
        )
        
        return ani
    
    @staticmethod
    def setup_interactive_visualization(fig, ax, sdf, domain_size=5.0):
        """Set up interactive controls for the visualization"""
        # Create a panel for controls
        control_ax = fig.add_axes([0.25, 0.01, 0.5, 0.05])
        
        # Add a slider for the visualization effect strength
        # effect_slider = Slider(
        #     control_ax, 'Effect', 0.0, 1.0, 
        #     valinit=0.5, 
        #     valstep=0.01,
        #     color='#58A6FF'
        # )
        
        # Add visualization style selector
        style_ax = fig.add_axes([0.02, 0.25, 0.1, 0.5])
        style_radio = RadioButtons(
            style_ax, 
            ['Standard', 'Hologram', 'Neon', 'Heatmap', 'Electric'],
            activecolor='#58A6FF'
        )
        
        # Store the SDF for later access
        ax.sdf_data = sdf
        ax.sdf_extent = [-domain_size, domain_size, -domain_size, domain_size]
        
        # Initial visualization (standard)
        im = ax.imshow(
            np.zeros_like(sdf), 
            extent=ax.sdf_extent,
            origin='lower'
        )
        
        # Add initial zero contour
        contour = ax.contour(
            sdf, 
            levels=[0], 
            colors=['white'], 
            linewidths=2,
            extent=ax.sdf_extent
        )
        
        # Function to update visualization based on selected style
        def update_visualization(label=None):
            # strength = effect_slider.val
            style = style_radio.value_selected if label is None else label
            
            if style == 'Standard':
                # Standard visualization with contour plot
                colors = [(0, 0, 1), (1, 1, 1), (1, 0, 0)]
                cmap = LinearSegmentedColormap.from_list("sdf_cmap", colors, N=100)
                
                # Clear previous image
                im.set_data(sdf)
                im.set_cmap(cmap)
                im.set_clim(-domain_size/2, domain_size/2)
                
            elif style == 'Hologram':
                # Holographic effect
                holo = AdvancedVisualization.create_holographic_effect(sdf, domain_size)
                im.set_data(holo)
                
            elif style == 'Neon':
                # Neon wireframe effect
                neon = AdvancedVisualization.create_neon_wireframe(sdf, domain_size)
                im.set_data(neon)
                
            elif style == 'Heatmap':
                # Heatmap visualization
                heatmap = AdvancedVisualization.create_heatmap_visualization(sdf, domain_size)
                im.set_data(heatmap)
                
            elif style == 'Electric':
                # Electric field visualization
                electric = AdvancedVisualization.create_electric_field_visualization(sdf, domain_size)
                im.set_data(electric)
            
            # Update contours
            for collection in contour.collections:
                collection.remove()
            
            # Adjust contour based on effect strength
            contour_new = ax.contour(
                sdf, 
                levels=[0], 
                colors=['white'], 
                linewidths=1 + strength * 2,
                extent=ax.sdf_extent
            )
            
            # Add glow effect based on strength
            if strength > 0.3:
                # Add glow layers
                glow_alpha = strength * 0.8
                glow_colors = [(1, 1, 1, glow_alpha * a) for a in [0.8, 0.5, 0.3, 0.1]]
                glow_widths = [(1 + strength * 2) * (1 + i*0.5) for i in range(4)]
                
                for i in range(len(glow_colors)):
                    ax.contour(
                        sdf, 
                        levels=[0], 
                        colors=[glow_colors[i]], 
                        linewidths=glow_widths[i],
                        extent=ax.sdf_extent
                    )
            
            fig.canvas.draw_idle()
        
        # Connect the update function to the controls
        # effect_slider.on_changed(lambda val: update_visualization())
        # style_radio.on_clicked(update_visualization)
        effect_slider = None
        
        # Initial update
        update_visualization()
        
        return effect_slider, style_radio