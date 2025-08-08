import os
import platform
import subprocess
from threading import Thread
from PIL import Image

DEBUG_MODE = os.environ.get("DEBUG_MODE", "0") == "1" or platform.system() == "Windows"

if not DEBUG_MODE:
    from inky.auto import auto

class DisplayService:
    def __init__(self):
        self.screenshots_dir = os.path.join(os.path.dirname(__file__), 'screenshots')
        os.makedirs(self.screenshots_dir, exist_ok=True)
        self.screenshot_path = os.path.join(self.screenshots_dir, 'screenshot.png')
        
        # Initialize inky display if not in debug mode
        if not DEBUG_MODE:
            self.inky = auto(ask_user=True, verbose=True)
        else:
            self.inky = None
    
    def display_screenshot(self, filepath, saturation=0.0):
        """Display a screenshot on the Inky Impression display.

        Args:
            filepath: Path to the screenshot file.
            saturation: Color saturation level (default: 0.5)
        """
        if DEBUG_MODE or not self.inky:
            print(f"Debug mode: Would display {filepath} on e-ink display")
            return
        
        image = Image.open(filepath)
        resized_image = image.resize(self.inky.resolution)

        try:
            self.inky.set_image(resized_image, saturation=saturation)
        except TypeError:
            self.inky.set_image(resized_image)

        self.inky.show()
    
    def take_screenshot_and_update_display(self):
        """Take a screenshot of the weather dashboard using headless Chromium."""
        try:
            url = "http://localhost:8080"
            
            if platform.system() == "Windows":
                cmd = [
                    'chrome',
                    '--headless',
                    '--disable-gpu',
                    '--window-size=800,400',
                    '--screenshot=' + self.screenshot_path,
                    url
                ]
            else:
                cmd = [
                    'chromium-browser',
                    '--headless',
                    '--disable-gpu',
                    '--window-size=800,400',
                    '--screenshot=' + self.screenshot_path,
                    url
                ]
                
            subprocess.run(cmd, check=True)
            
            # Display the screenshot on e-ink display
            self.display_screenshot(self.screenshot_path)
            
            if DEBUG_MODE:
                print(f"Debug mode: Screenshot saved to {self.screenshot_path}")
            
            return True
        except Exception as e:
            print(f"Error taking screenshot: {e}")
            return False
    
    def update_display_async(self):
        """Update display in a separate thread"""
        Thread(target=self.take_screenshot_and_update_display).start()