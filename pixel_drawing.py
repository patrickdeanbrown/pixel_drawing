#!/usr/bin/env python3
"""
Pixel Drawing - A simple pixel art application for creating retro game assets.
Cross-platform GUI application built with Tkinter.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
from PIL import Image, ImageTk, ImageDraw
import json
import os
import math
from typing import Tuple, Optional, List


class PixelCanvas:
    """Canvas widget for pixel art drawing with grid and zoom functionality."""
    
    def __init__(self, parent, width: int = 32, height: int = 32, pixel_size: int = 16):
        self.parent = parent
        self.grid_width = width
        self.grid_height = height
        self.pixel_size = pixel_size
        self.current_color = "#000000"
        self.current_tool = "brush"
        
        # Create the canvas
        canvas_width = self.grid_width * self.pixel_size
        canvas_height = self.grid_height * self.pixel_size
        
        self.canvas = tk.Canvas(
            parent,
            width=canvas_width,
            height=canvas_height,
            bg="white",
            bd=1,
            relief="solid"
        )
        
        # Initialize pixel data
        self.pixels = {}
        for x in range(self.grid_width):
            for y in range(self.grid_height):
                self.pixels[(x, y)] = "#FFFFFF"
        
        # Bind mouse events
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        
        self.draw_grid()
        self.canvas.pack(padx=10, pady=10)
    
    def draw_grid(self):
        """Draw the pixel grid on the canvas."""
        self.canvas.delete("all")
        
        # Draw pixels
        for (x, y), color in self.pixels.items():
            x1 = x * self.pixel_size
            y1 = y * self.pixel_size
            x2 = x1 + self.pixel_size
            y2 = y1 + self.pixel_size
            
            self.canvas.create_rectangle(
                x1, y1, x2, y2,
                fill=color,
                outline="#CCCCCC",
                width=1
            )
    
    def get_pixel_coords(self, canvas_x: int, canvas_y: int) -> Tuple[int, int]:
        """Convert canvas coordinates to pixel grid coordinates."""
        pixel_x = canvas_x // self.pixel_size
        pixel_y = canvas_y // self.pixel_size
        return pixel_x, pixel_y
    
    def on_click(self, event):
        """Handle mouse click events."""
        pixel_x, pixel_y = self.get_pixel_coords(event.x, event.y)
        
        if 0 <= pixel_x < self.grid_width and 0 <= pixel_y < self.grid_height:
            if self.current_tool == "brush":
                self.paint_pixel(pixel_x, pixel_y)
            elif self.current_tool == "fill":
                self.fill_bucket(pixel_x, pixel_y)
    
    def on_drag(self, event):
        """Handle mouse drag events for continuous drawing."""
        if self.current_tool == "brush":
            pixel_x, pixel_y = self.get_pixel_coords(event.x, event.y)
            if 0 <= pixel_x < self.grid_width and 0 <= pixel_y < self.grid_height:
                self.paint_pixel(pixel_x, pixel_y)
    
    def paint_pixel(self, x: int, y: int):
        """Paint a single pixel with the current color."""
        self.pixels[(x, y)] = self.current_color
        self.draw_pixel(x, y)
    
    def draw_pixel(self, x: int, y: int):
        """Redraw a single pixel on the canvas."""
        x1 = x * self.pixel_size
        y1 = y * self.pixel_size
        x2 = x1 + self.pixel_size
        y2 = y1 + self.pixel_size
        
        self.canvas.create_rectangle(
            x1, y1, x2, y2,
            fill=self.pixels[(x, y)],
            outline="#CCCCCC",
            width=1
        )
    
    def fill_bucket(self, start_x: int, start_y: int):
        """Fill connected pixels of the same color."""
        target_color = self.pixels[(start_x, start_y)]
        if target_color == self.current_color:
            return
        
        stack = [(start_x, start_y)]
        visited = set()
        
        while stack:
            x, y = stack.pop()
            if (x, y) in visited:
                continue
            if x < 0 or x >= self.grid_width or y < 0 or y >= self.grid_height:
                continue
            if self.pixels[(x, y)] != target_color:
                continue
            
            visited.add((x, y))
            self.pixels[(x, y)] = self.current_color
            
            # Add neighboring pixels to stack
            stack.extend([(x+1, y), (x-1, y), (x, y+1), (x, y-1)])
        
        self.draw_grid()
    
    def clear_canvas(self):
        """Clear all pixels to white."""
        for key in self.pixels:
            self.pixels[key] = "#FFFFFF"
        self.draw_grid()
    
    def resize_canvas(self, new_width: int, new_height: int):
        """Resize the canvas while preserving existing pixels."""
        new_pixels = {}
        
        # Copy existing pixels and fill new areas with white
        for x in range(new_width):
            for y in range(new_height):
                if x < self.grid_width and y < self.grid_height:
                    new_pixels[(x, y)] = self.pixels.get((x, y), "#FFFFFF")
                else:
                    new_pixels[(x, y)] = "#FFFFFF"
        
        self.grid_width = new_width
        self.grid_height = new_height
        self.pixels = new_pixels
        
        # Resize the canvas widget
        canvas_width = self.grid_width * self.pixel_size
        canvas_height = self.grid_height * self.pixel_size
        self.canvas.config(width=canvas_width, height=canvas_height)
        
        self.draw_grid()


class PixelDrawingApp:
    """Main application class for the Pixel Drawing app."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Pixel Drawing - Retro Game Asset Creator")
        self.root.resizable(False, False)
        
        # Initialize variables
        self.current_file = None
        self.current_color = "#000000"
        self.recent_colors = ["#FFFFFF"] * 6  # Last 6 colors, start with white
        
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the user interface."""
        # Create main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create toolbar
        self.create_toolbar(main_frame)
        
        # Create canvas frame
        canvas_frame = ttk.Frame(main_frame)
        canvas_frame.pack(side="left", fill="both", expand=True)
        
        # Create pixel canvas
        self.canvas = PixelCanvas(canvas_frame, 32, 32, 16)
        
        # Create side panel
        self.create_side_panel(main_frame)
        
    def create_toolbar(self, parent):
        """Create the toolbar with menu items."""
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill="x", pady=(0, 10))
        
        # File operations
        ttk.Button(toolbar, text="New", command=self.new_file).pack(side="left", padx=(0, 5))
        ttk.Button(toolbar, text="Open", command=self.open_file).pack(side="left", padx=(0, 5))
        ttk.Button(toolbar, text="Save", command=self.save_file).pack(side="left", padx=(0, 5))
        ttk.Button(toolbar, text="Save As", command=self.save_as_file).pack(side="left", padx=(0, 5))
        
        # Separator
        ttk.Separator(toolbar, orient="vertical").pack(side="left", fill="y", padx=10)
        
        # Export
        ttk.Button(toolbar, text="Export PNG", command=self.export_png).pack(side="left", padx=(0, 5))
        
    def create_side_panel(self, parent):
        """Create the side panel with tools and options."""
        side_panel = ttk.Frame(parent)
        side_panel.pack(side="right", fill="y", padx=(10, 0))
        
        # Tools section
        tools_frame = ttk.LabelFrame(side_panel, text="Tools")
        tools_frame.pack(fill="x", pady=(0, 10))
        
        self.tool_var = tk.StringVar(value="brush")
        ttk.Radiobutton(tools_frame, text="Brush", variable=self.tool_var, 
                       value="brush", command=self.change_tool).pack(anchor="w")
        ttk.Radiobutton(tools_frame, text="Fill Bucket", variable=self.tool_var, 
                       value="fill", command=self.change_tool).pack(anchor="w")
        
        # Color section
        color_frame = ttk.LabelFrame(side_panel, text="Color")
        color_frame.pack(fill="x", pady=(0, 10))
        
        # Current color display
        self.color_display = tk.Label(color_frame, bg=self.current_color, 
                                     width=10, height=2, relief="solid", bd=1)
        self.color_display.pack(pady=5)
        
        ttk.Button(color_frame, text="Choose Color", 
                  command=self.choose_color).pack(pady=2)
        
        # Base color palette (16 colors)
        palette_frame = tk.Frame(color_frame)
        palette_frame.pack(pady=5)
        tk.Label(palette_frame, text="Base Colors:", font=("Arial", 8)).pack(anchor="w")
        
        base_colors = [
            "#000000", "#FFFFFF", "#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FF00FF", "#00FFFF",
            "#800000", "#808080", "#800080", "#008000", "#000080", "#808000", "#FFA500", "#FFC0CB"
        ]
        
        self.create_color_grid(palette_frame, base_colors, 8, 2)
        
        # Recent colors
        recent_frame = tk.Frame(color_frame)
        recent_frame.pack(pady=5)
        tk.Label(recent_frame, text="Recent Colors:", font=("Arial", 8)).pack(anchor="w")
        
        self.recent_color_buttons = []
        self.create_recent_colors_grid(recent_frame)
        
        # Color wheel
        wheel_frame = tk.Frame(color_frame)
        wheel_frame.pack(pady=5)
        tk.Label(wheel_frame, text="Color Wheel:", font=("Arial", 8)).pack(anchor="w")
        
        self.create_color_wheel(wheel_frame)
        
        # Canvas size section
        size_frame = ttk.LabelFrame(side_panel, text="Canvas Size")
        size_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(size_frame, text="Width:").pack(anchor="w")
        self.width_var = tk.StringVar(value="32")
        ttk.Entry(size_frame, textvariable=self.width_var, width=10).pack(pady=(0, 5))
        
        ttk.Label(size_frame, text="Height:").pack(anchor="w")
        self.height_var = tk.StringVar(value="32")
        ttk.Entry(size_frame, textvariable=self.height_var, width=10).pack(pady=(0, 5))
        
        ttk.Button(size_frame, text="Resize Canvas", 
                  command=self.resize_canvas).pack(pady=5)
        
        # Actions section
        actions_frame = ttk.LabelFrame(side_panel, text="Actions")
        actions_frame.pack(fill="x")
        
        ttk.Button(actions_frame, text="Clear Canvas", 
                  command=self.clear_canvas).pack(pady=2, fill="x")
        
    def change_tool(self):
        """Change the current drawing tool."""
        self.canvas.current_tool = self.tool_var.get()
        
    def create_color_grid(self, parent, colors, cols, rows):
        """Create a grid of color buttons."""
        grid_frame = tk.Frame(parent)
        grid_frame.pack()
        
        for i, color in enumerate(colors):
            row = i // cols
            col = i % cols
            
            # Create frame with padding for hover effect
            btn_frame = tk.Frame(grid_frame, width=24, height=24)
            btn_frame.grid(row=row, column=col, padx=2, pady=2)
            btn_frame.grid_propagate(False)
            
            btn = tk.Button(btn_frame, bg=color, relief="solid", bd=1,
                           command=lambda c=color: self.set_color(c))
            btn.place(relx=0.5, rely=0.5, anchor="center", width=18, height=18)
            
            # Add hover effects that don't change size
            def on_enter(e, button=btn, frame=btn_frame):
                button.config(bd=3)
                frame.config(highlightbackground="#0066CC", highlightthickness=2)
            
            def on_leave(e, button=btn, frame=btn_frame):
                button.config(bd=1)
                frame.config(highlightthickness=0)
            
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)
    
    def create_recent_colors_grid(self, parent):
        """Create grid for recent colors."""
        grid_frame = tk.Frame(parent)
        grid_frame.pack()
        
        for i in range(6):
            row = i // 6
            col = i % 6
            
            # Create frame with padding for hover effect
            btn_frame = tk.Frame(grid_frame, width=24, height=24)
            btn_frame.grid(row=row, column=col, padx=2, pady=2)
            btn_frame.grid_propagate(False)
            
            btn = tk.Button(btn_frame, bg=self.recent_colors[i], relief="solid", bd=1,
                           command=lambda idx=i: self.set_color(self.recent_colors[idx]))
            btn.place(relx=0.5, rely=0.5, anchor="center", width=18, height=18)
            
            # Add hover effects that don't change size
            def on_enter(e, button=btn, frame=btn_frame):
                button.config(bd=3)
                frame.config(highlightbackground="#0066CC", highlightthickness=2)
            
            def on_leave(e, button=btn, frame=btn_frame):
                button.config(bd=1)
                frame.config(highlightthickness=0)
            
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)
            
            self.recent_color_buttons.append((btn, btn_frame))
    
    def create_color_wheel(self, parent):
        """Create a smooth gradient color wheel like Photoshop/Paint."""
        wheel_size = 150
        self.color_wheel = tk.Canvas(parent, width=wheel_size, height=wheel_size, 
                                   bg=parent.cget('bg'), highlightthickness=0)
        self.color_wheel.pack(pady=5)
        
        center = wheel_size // 2
        outer_radius = center - 10
        inner_radius = 20
        
        # Create smooth color wheel with many small segments
        for angle in range(360):
            # Calculate hue from angle - adjust so red is at top (0 degrees)
            # Standard color wheel has red at top, going clockwise
            adjusted_angle = (90 - angle) % 360  # Start with red at top
            hue = adjusted_angle / 360.0
            
            # Draw radial gradient from center to edge
            for radius in range(inner_radius, outer_radius, 2):
                # Calculate saturation based on distance from center
                saturation = min(1.0, (radius - inner_radius) / (outer_radius - inner_radius))
                
                # Full brightness for the main wheel
                value = 1.0
                
                # Convert HSV to RGB
                rgb = self.hsv_to_rgb(hue, saturation, value)
                color = "#{:02x}{:02x}{:02x}".format(int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255))
                
                # Calculate start and end points for this segment
                x1 = center + radius * math.cos(math.radians(angle))
                y1 = center + radius * math.sin(math.radians(angle))
                x2 = center + (radius + 2) * math.cos(math.radians(angle))
                y2 = center + (radius + 2) * math.sin(math.radians(angle))
                
                # Draw the color segment
                self.color_wheel.create_line(x1, y1, x2, y2, fill=color, width=3)
        
        # Add white center for easy white selection
        self.color_wheel.create_oval(center - inner_radius, center - inner_radius,
                                   center + inner_radius, center + inner_radius,
                                   fill="white", outline="#CCCCCC", width=2)
        
        # Add brightness/saturation square below the wheel
        square_size = 100
        square_y = wheel_size + 10
        self.brightness_square = tk.Canvas(parent, width=square_size, height=square_size, 
                                         bg=parent.cget('bg'), highlightthickness=0)
        self.brightness_square.pack(pady=5)
        
        # Draw brightness/saturation gradient square
        self.current_hue = 0.0  # Will be updated when wheel is clicked
        self.draw_brightness_square()
        
        # Bind click events
        self.color_wheel.bind("<Button-1>", self.on_wheel_click)
        self.brightness_square.bind("<Button-1>", self.on_brightness_click)
    
    def hsv_to_rgb(self, h, s, v):
        """Convert HSV to RGB."""
        if s == 0.0:
            return (v, v, v)
        
        i = int(h * 6.0)
        f = (h * 6.0) - i
        p, q, t = v * (1.0 - s), v * (1.0 - s * f), v * (1.0 - s * (1.0 - f))
        
        if i % 6 == 0:
            return (v, t, p)
        elif i % 6 == 1:
            return (q, v, p)
        elif i % 6 == 2:
            return (p, v, t)
        elif i % 6 == 3:
            return (p, q, v)
        elif i % 6 == 4:
            return (t, p, v)
        else:
            return (v, p, q)
    
    def draw_brightness_square(self):
        """Draw the brightness/saturation selection square."""
        square_size = 100
        self.brightness_square.delete("all")
        
        # Draw gradient square for current hue
        for x in range(0, square_size, 2):
            for y in range(0, square_size, 2):
                # Calculate saturation (left to right) and value/brightness (top to bottom)
                saturation = x / square_size
                value = 1.0 - (y / square_size)  # Top is bright, bottom is dark
                
                # Convert HSV to RGB using current hue
                rgb = self.hsv_to_rgb(self.current_hue, saturation, value)
                color = "#{:02x}{:02x}{:02x}".format(int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255))
                
                # Draw small rectangle for this color
                self.brightness_square.create_rectangle(x, y, x+2, y+2, fill=color, outline=color)
    
    def on_wheel_click(self, event):
        """Handle color wheel click."""
        wheel_size = 150
        center = wheel_size // 2
        x = event.x - center
        y = event.y - center
        
        # Calculate distance from center
        distance = math.sqrt(x*x + y*y)
        inner_radius = 20
        outer_radius = center - 10
        
        if distance < inner_radius:  # Center white area
            self.set_color("#FFFFFF")
            return
        elif distance < outer_radius:  # Color wheel area
            # Calculate angle in degrees
            angle_rad = math.atan2(y, x)
            angle_deg = math.degrees(angle_rad)
            
            # Convert to the same coordinate system as the wheel drawing
            # atan2 gives us -180 to 180, convert to 0-360
            if angle_deg < 0:
                angle_deg += 360
            
            # Apply the same transformation as in drawing: red at top
            adjusted_angle = (90 - angle_deg) % 360
            hue = adjusted_angle / 360.0
            
            # Calculate saturation based on distance
            saturation = min(1.0, (distance - inner_radius) / (outer_radius - inner_radius))
            
            # Full brightness
            value = 1.0
            
            # Update current hue and redraw brightness square
            self.current_hue = hue
            self.draw_brightness_square()
            
            # Convert to RGB and set color
            rgb = self.hsv_to_rgb(hue, saturation, value)
            color = "#{:02x}{:02x}{:02x}".format(int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255))
            self.set_color(color)
    
    def on_brightness_click(self, event):
        """Handle brightness/saturation square click."""
        square_size = 100
        
        # Calculate saturation and value from click position
        saturation = min(1.0, event.x / square_size)
        value = max(0.0, 1.0 - (event.y / square_size))
        
        # Use current hue with new saturation and value
        rgb = self.hsv_to_rgb(self.current_hue, saturation, value)
        color = "#{:02x}{:02x}{:02x}".format(int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255))
        self.set_color(color)
    
    def set_color(self, color):
        """Set the current color and update recent colors."""
        # Add to recent colors if it's not already there
        if color != self.current_color and color not in self.recent_colors:
            self.recent_colors.insert(0, color)
            self.recent_colors = self.recent_colors[:6]  # Keep only last 6
            self.update_recent_colors_display()
        
        self.current_color = color
        self.canvas.current_color = self.current_color
        self.color_display.config(bg=self.current_color)
    
    def update_recent_colors_display(self):
        """Update the recent colors grid display."""
        for i, (btn, frame) in enumerate(self.recent_color_buttons):
            btn.config(bg=self.recent_colors[i])
            btn.config(command=lambda idx=i: self.set_color(self.recent_colors[idx]))
    
    def choose_color(self):
        """Open color chooser dialog."""
        color = colorchooser.askcolor(color=self.current_color)
        if color[1]:  # If a color was selected
            self.set_color(color[1])
    
    def new_file(self):
        """Create a new file."""
        if messagebox.askyesno("New File", "Are you sure? Unsaved changes will be lost."):
            self.canvas.clear_canvas()
            self.current_file = None
            self.root.title("Pixel Drawing - Retro Game Asset Creator")
    
    def open_file(self):
        """Open a pixel art file."""
        file_path = filedialog.askopenfilename(
            title="Open Pixel Art File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                # Restore canvas size and pixels
                self.canvas.grid_width = data["width"]
                self.canvas.grid_height = data["height"]
                self.canvas.pixels = {tuple(map(int, k.split(','))): v 
                                    for k, v in data["pixels"].items()}
                
                # Update UI
                self.width_var.set(str(data["width"]))
                self.height_var.set(str(data["height"]))
                
                # Resize canvas widget
                canvas_width = self.canvas.grid_width * self.canvas.pixel_size
                canvas_height = self.canvas.grid_height * self.canvas.pixel_size
                self.canvas.canvas.config(width=canvas_width, height=canvas_height)
                
                self.canvas.draw_grid()
                self.current_file = file_path
                self.root.title(f"Pixel Drawing - {os.path.basename(file_path)}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open file: {str(e)}")
    
    def save_file(self):
        """Save the current pixel art."""
        if self.current_file:
            self._save_to_file(self.current_file)
        else:
            self.save_as_file()
    
    def save_as_file(self):
        """Save the current pixel art with a new filename."""
        file_path = filedialog.asksaveasfilename(
            title="Save Pixel Art File",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            self._save_to_file(file_path)
            self.current_file = file_path
            self.root.title(f"Pixel Drawing - {os.path.basename(file_path)}")
    
    def _save_to_file(self, file_path: str):
        """Save pixel data to a JSON file."""
        try:
            data = {
                "width": self.canvas.grid_width,
                "height": self.canvas.grid_height,
                "pixels": {f"{x},{y}": color for (x, y), color in self.canvas.pixels.items()}
            }
            
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
                
            messagebox.showinfo("Success", "File saved successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {str(e)}")
    
    def export_png(self):
        """Export the pixel art as a PNG image."""
        file_path = filedialog.asksaveasfilename(
            title="Export as PNG",
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                # Create PIL image
                img = Image.new("RGB", (self.canvas.grid_width, self.canvas.grid_height), "white")
                
                for (x, y), color in self.canvas.pixels.items():
                    # Convert hex color to RGB
                    if color.startswith("#"):
                        color = color[1:]
                    rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
                    img.putpixel((x, y), rgb)
                
                img.save(file_path)
                messagebox.showinfo("Success", "PNG exported successfully!")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export PNG: {str(e)}")
    
    def resize_canvas(self):
        """Resize the canvas based on user input."""
        try:
            new_width = int(self.width_var.get())
            new_height = int(self.height_var.get())
            
            if new_width <= 0 or new_height <= 0:
                raise ValueError("Dimensions must be positive")
            
            if new_width > 256 or new_height > 256:
                if not messagebox.askyesno("Large Canvas", 
                                         "Large canvases may affect performance. Continue?"):
                    return
            
            self.canvas.resize_canvas(new_width, new_height)
            
        except ValueError as e:
            messagebox.showerror("Error", "Invalid canvas dimensions")
    
    def clear_canvas(self):
        """Clear the canvas after confirmation."""
        if messagebox.askyesno("Clear Canvas", "Are you sure you want to clear the canvas?"):
            self.canvas.clear_canvas()
    
    def run(self):
        """Start the application."""
        self.root.mainloop()


def main():
    """Main entry point."""
    app = PixelDrawingApp()
    app.run()


if __name__ == "__main__":
    main()