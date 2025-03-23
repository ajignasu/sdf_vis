#!/usr/bin/env python3
"""
Futuristic SDF Visualizer - Main Launcher
A sleek, modern interface for visualizing Signed Distance Functions and boolean operations
"""

import os
import sys
import tkinter as tk
import numpy as np

# Ensure all required modules are available
try:
    import matplotlib
    import scipy
    from PIL import Image, ImageTk
except ImportError as e:
    print(f"Error: Missing required module - {e}")
    print("Please install required dependencies with: pip install numpy matplotlib scipy pillow")
    sys.exit(1)

# Import application modules
try:
    from splash_screen import start_with_splash
    from futuristic_theme import FuturisticTheme
    from futuristic_sdf_visualizer import FuturisticSDFVisualizer
except ImportError as e:
    print(f"Error: Could not import application modules - {e}")
    print("Make sure all files are in the correct location.")
    sys.exit(1)

def main(root=None):
    """Main application entry point"""
    if root is None:
        # Create the Tkinter root if not provided (when not using splash screen)
        root = tk.Tk()
        FuturisticTheme.apply_theme(root)
        root.title("Futuristic SDF Visualizer")
    
    # Create the SDF visualizer application
    try:
        app = FuturisticSDFVisualizer(root)
        
        # Configure window
        root.geometry("1280x800")
        root.minsize(800, 600)
        
        # Start the mainloop if not already running
        if not getattr(root, '_in_mainloop', False):
            root._in_mainloop = True
            root.mainloop()
        
        return app
    except Exception as e:
        print(f"Error starting application: {e}")
        import traceback
        traceback.print_exc()
        if root is not None:
            root.destroy()
        sys.exit(1)

if __name__ == "__main__":
    # Set up error handling
    def show_error(exc_type, exc_value, exc_traceback):
        import traceback
        print("An error occurred:")
        traceback.print_exception(exc_type, exc_value, exc_traceback)
        
        # Show error dialog
        if 'tk' in sys.modules:
            import tkinter.messagebox as messagebox
            messagebox.showerror("Error", f"An error occurred:\n{exc_value}")
    
    # Set custom exception handler
    sys.excepthook = show_error
    
    # Check command-line arguments
    if len(sys.argv) > 1 and sys.argv[1] == "--no-splash":
        # Start without splash screen
        print("Starting without splash screen...")
        main()
    else:
        # Start with splash screen
        try:
            print("Starting with splash screen...")
            start_with_splash(main)
        except Exception as e:
            print(f"Error in splash screen: {e}")
            print("Falling back to direct start...")
            main()