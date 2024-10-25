import tkinter as tk
from tkinter import Canvas
import numpy as np
from PIL import Image
import os
from datetime import datetime
import mss
from screeninfo import get_monitors

class ScreenshotSelector:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Selector de Captura de Pantalla")
        self.root.overrideredirect(True) 

        self.monitors = get_monitors()
        self.monitor = self.get_total_monitor_geometry()
        self.root.geometry(f"{self.monitor['width']}x{self.monitor['height']}+{self.monitor['x']}+{self.monitor['y']}")


        self.canvas = Canvas(self.root, bg='black', cursor='cross', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

  
        self.root.attributes('-alpha', 0.5)

        self.start_x = None
        self.start_y = None
        self.rect = None
        self.image_np = None  
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

        self.root.mainloop()

    def get_total_monitor_geometry(self):
        x_min = min(m.x for m in self.monitors)
        y_min = min(m.y for m in self.monitors)
        x_max = max(m.x + m.width for m in self.monitors)
        y_max = max(m.y + m.height for m in self.monitors)

        return {
            'x': x_min,
            'y': y_min,
            'width': x_max - x_min,
            'height': y_max - y_min
        }

    def on_button_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, event.x, event.y, outline='red', width=2)

    def on_mouse_drag(self, event):
        self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)

    def on_button_release(self, event):
        self.capture_screenshot(event)

    def capture_screenshot(self, event):
        self.root.withdraw()
        x1 = min(self.start_x, event.x)
        y1 = min(self.start_y, event.y)
        x2 = max(self.start_x, event.x)
        y2 = max(self.start_y, event.y)

        global_x1 = self.root.winfo_rootx() + x1
        global_y1 = self.root.winfo_rooty() + y1
        global_x2 = self.root.winfo_rootx() + x2
        global_y2 = self.root.winfo_rooty() + y2

        with mss.mss() as sct:
            bbox = {
                'top': global_y1,
                'left': global_x1,
                'width': global_x2 - global_x1,
                'height': global_y2 - global_y1
            }
            image = sct.grab(bbox)
            img = Image.frombytes("RGB", image.size, image.rgb)


            self.image_np = np.array(img)

        self.exit_app()

    def exit_app(self):
        self.root.quit()