# Futuristic SDF Visualizer

A sleek, modern tool for visualizing and experimenting with Signed Distance Functions (SDFs) in 2D.

![SDF Visualizer Screenshot](test.png)

## Features

- **Interactive Shape Creation**: Add circles, rectangles, triangles, and lines with real-time visualization
- **Boolean Operations**: Union, intersection, difference, and smooth union operations between shapes
- **Multiple Visualization Styles**: 
  - Standard (color-mapped)
  - Holographic projection
  - Neon wireframe
  - Thermal heatmap
  - Electric field
- **Signed/Unsigned Mode**: Toggle between signed and unsigned distance field visualization
- **Animation**: Animated pulsing visualization option
- **Export**: Save visualizations as images with customizable options

## Installation

### Prerequisites

- Python 3.7+
- Required packages:
  - numpy
  - matplotlib
  - scipy
  - Pillow (PIL)
  - tkinter (usually included with Python)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/ajignasu/sdf_vis.git
   cd sdf-vis
   ```

2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv sdf-venv
   ```

3. Activate the virtual environment:
   - Windows: `sdf-venv\Scripts\activate`
   - macOS/Linux: `source sdf-venv/bin/activate`

4. Install dependencies:
   ```bash
   pip install numpy matplotlib scipy pillow
   ```

## Usage

### Starting the Application

Run the main script:

```bash
python main.py
```

For a version without the splash screen:

```bash
python main.py --no-splash
```

### Creating Shapes

1. Click one of the shape buttons in the "ADD SHAPE" section:
   - Circle
   - Rectangle
   - Triangle
   - Line

2. The shape will appear in the visualization area with default parameters

3. Select the shape in the shapes list to edit its properties

4. Modify parameters like position, size, and rotation in the properties panel

### Applying Boolean Operations

1. Add multiple shapes to your scene

2. Select a boolean operation from the "BOOLEAN OPERATION" section:
   - None (default display of all shapes)
   - Union (combine shapes)
   - Intersection (show only where shapes overlap)
   - Difference (subtract one shape from another)
   - Smooth Union (blend shapes together smoothly)

### Visualization Options

1. Choose a visualization style from the dropdown:
   - Standard
   - Hologram
   - Neon
   - Heatmap
   - Electric

2. Toggle "Unsigned Distance" to switch between signed and unsigned SDF visualization

3. Toggle "Animation" to enable a pulsing animation effect

### Saving Visualizations

1. Click the "Save Image" button

2. Choose your save options:
   - Include axes and labels
   - Include title
   - Include grid
   - DPI (resolution)

3. Select a save location and format (PNG, JPEG, SVG, or PDF)

## Understanding SDF Visualization

- **Colors**: 
  - Blue: Inside shapes (negative distance)
  - White: Near boundaries (zero distance)
  - Red: Outside shapes (positive distance)

- **Unsigned Mode**:
  - Shows absolute distance from any point to the nearest boundary
  - White: Near boundaries (zero distance)
  - Red: Far from boundaries (large distance)

- **Contour Lines**:
  - White boundary lines show the exact shape outlines (zero level)

## Technical Details

### SDF Principles

Signed Distance Functions represent geometry by encoding the distance from any point to the nearest surface:
- Negative values indicate points inside the shape
- Positive values indicate points outside the shape
- Zero values occur exactly at the shape's boundary

### Boolean Operations

- **Union**: min(sdf1, sdf2)
- **Intersection**: max(sdf1, sdf2)
- **Difference**: max(sdf1, -sdf2)
- **Smooth Union**: Smooth interpolation between fields

## Troubleshooting

- **Visualization issues**: Try toggling between visualization styles
- **Performance problems**: Reduce the resolution in the code (default is 200)
- **Shape distortion**: Ensure coordinates are within the domain size (default ±5 units)

<!-- ## License

[MIT License](LICENSE) -->

## Acknowledgments

- Inigo Quilez for pioneering work on SDFs
- The matplotlib and numpy communities