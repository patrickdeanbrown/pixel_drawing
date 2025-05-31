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
        
        self.color_display = tk.Label(color_frame, bg=self.current_color, 
                                     width=10, height=2, relief="solid", bd=1)
        self.color_display.pack(pady=5)
        
        ttk.Button(color_frame, text="Choose Color", 
                  command=self.choose_color).pack(pady=5)
        
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
        
    def choose_color(self):
        """Open color chooser dialog."""
        color = colorchooser.askcolor(color=self.current_color)
        if color[1]:  # If a color was selected
            self.current_color = color[1]
            self.canvas.current_color = self.current_color
            self.color_display.config(bg=self.current_color)
    
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