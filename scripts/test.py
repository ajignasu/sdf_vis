# test_splash.py
import tkinter as tk
from tron_splash_screen import TronSplashScreen

def dummy_function(root):
    root.title("Main Application")
    label = tk.Label(root, text="Main App Started")
    label.pack(pady=20)

if __name__ == "__main__":
    root = tk.Tk()
    splash = TronSplashScreen(root, duration=3.0, callback=lambda: dummy_function(root))
    root.mainloop()