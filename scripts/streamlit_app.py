import streamlit as st
import subprocess
import sys
import os
import tempfile
from PIL import Image
import matplotlib.pyplot as plt

st.title("SDF Visualizer")
st.write("This is an online version of the SDF Visualizer tool")

# Create a button to launch the application
if st.button("Open SDF Visualizer in New Window"):
    # This will execute your script in a subprocess
    subprocess.Popen([sys.executable, "futuristic_sdf_visualizer.py"])
    st.success("Application launched! Check your taskbar for the new window.")

# Alternatively, show screenshots and documentation
st.header("How to use")
st.write("""
1. Click the button above to launch the full application
2. Use the shape tools to create SDFs
3. Explore different visualization styles
""")

# Display some example images
st.image("D:/Code/sdf_vis/data/test.png", caption="Example visualization")