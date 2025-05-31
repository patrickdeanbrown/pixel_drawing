# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a cross-platform pixel art application built with Python and Tkinter for creating retro game assets. The application allows users to create pixel art with brush and fill bucket tools, save projects as JSON files, and export to PNG format.

## Development Commands

### Running the Application
```bash
python pixel_drawing.py
```

### Installing Dependencies
```bash
pip install -r requirements.txt
```

### Installing the Package
```bash
pip install -e .
```

### Running via Console Script (after installation)
```bash
pixel-drawing
```

## Architecture

### Core Components

- **PixelCanvas**: The main drawing canvas widget that handles pixel grid rendering, mouse interactions, and drawing operations. Contains the pixel data structure and implements brush/fill bucket tools.
- **PixelDrawingApp**: Main application class that manages the UI layout, toolbar, side panel, file operations, and coordinates between UI elements and the canvas.

### Key Data Structures

- `pixels` dictionary: Maps (x, y) tuples to hex color strings, representing the entire pixel art
- Canvas grid system: Uses `pixel_size` to scale between logical pixels and screen pixels
- Tool system: String-based tool selection ("brush", "fill") with different mouse event behaviors

### File Format

Projects are saved as JSON with structure:
```json
{
  "width": 32,
  "height": 32, 
  "pixels": {"0,0": "#FFFFFF", "1,0": "#000000", ...}
}
```

### Drawing System

The application uses a coordinate transformation system where canvas pixel coordinates are divided by `pixel_size` to get logical grid coordinates. Drawing operations modify the `pixels` dictionary and trigger grid redraws. The fill bucket uses a flood-fill algorithm with a stack-based approach.