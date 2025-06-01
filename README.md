# Pixel Drawing - Retro Game Asset Creator

A modern, cross-platform pixel art application built with Python and PyQt6 for creating retro game assets. Features a professional interface with brush and fill bucket tools, color management, and efficient file handling.

## Features

### Drawing Tools
- **Brush Tool** - Paint individual pixels with precision
- **Fill Bucket** - Flood fill areas with selected colors
- **Real-time Preview** - See changes instantly as you draw

### User Interface
- Modern Qt-based interface with professional styling
- Tool selection with visual icons
- Color picker with recent colors palette
- Canvas size controls with validation
- Status bar with pixel coordinates and tool information

### File Operations
- **Project Files** - Save/load work as JSON files with full fidelity
- **PNG Export** - Export finished artwork as optimized PNG images
- **Auto-save** - Tracks unsaved changes and prevents data loss
- **Error Handling** - Comprehensive validation and user-friendly error messages

### Performance & Usability
- **Memory Efficient** - Sparse pixel storage for large canvases
- **Optimized Rendering** - Dirty region tracking for smooth performance
- **Keyboard Shortcuts** - Quick access to all major functions
- **Mouse Wheel Zoom** - Ctrl+wheel to zoom in/out (4x to 64x)
- **Responsive UI** - Professional layout that scales properly

## Installation

### Requirements
- Python 3.8 or higher
- PyQt6
- Pillow (PIL)

### Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/patrickdeanbrown/pixel_drawing.git
   cd pixel_drawing
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python pixel_drawing_qt.py
   ```

### Alternative Installation
Install as a package for command-line access:
```bash
pip install -e .
pixel-drawing
```

## Usage

### Getting Started
1. Launch the application
2. Select a drawing tool (Brush or Fill Bucket)
3. Choose a color using the color picker
4. Click and drag on the canvas to draw
5. Save your work using File > Save or Ctrl+S

### Keyboard Shortcuts
- **File Operations:**
  - `Ctrl+N` - New file
  - `Ctrl+O` - Open file
  - `Ctrl+S` - Save file
  - `Ctrl+Shift+S` - Save as
  - `Ctrl+E` - Export PNG
  - `Ctrl+Q` - Quit application

- **Tools:**
  - `B` - Switch to Brush tool
  - `F` - Switch to Fill Bucket tool

- **Canvas:**
  - `Ctrl+Del` - Clear canvas
  - `Ctrl+Mouse Wheel` - Zoom in/out

### Color Management
- Click the color display to open the color picker
- Recent colors are automatically saved in the palette
- Click any recent color button to quickly select it
- Colors are displayed in uppercase hex format

### Canvas Operations
- Adjust canvas size using the width/height controls
- Canvas can be resized from 1x1 to 256x256 pixels
- Existing artwork is preserved when resizing
- Large canvas warnings help prevent performance issues

## File Formats

### Project Files (.json)
The application saves projects in a human-readable JSON format:
```json
{
  "width": 32,
  "height": 32,
  "pixels": {
    "0,0": "#FFFFFF",
    "1,0": "#000000"
  }
}
```

### Export Formats
- **PNG** - Optimized for web and game engines
- **1:1 pixel mapping** - Each logical pixel becomes one PNG pixel
- **Transparency preserved** - Clean export for sprite work

## Architecture

The application follows a modern MVC (Model-View-Controller) architecture:

- **PixelArtModel** - Core data management and business logic
- **PixelCanvas** - Interactive drawing interface and view
- **PixelDrawingApp** - Main controller and UI coordination
- **FileService** - Handles all file I/O operations
- **Tool System** - Extensible drawing tool architecture

Key design patterns:
- Signal/slot communication for decoupled components
- Command pattern foundation for future undo/redo
- Sparse data structures for memory efficiency
- Comprehensive error handling and validation

## Development

### Code Quality
- **100% type coverage** with comprehensive type hints
- **Extensive documentation** with Args/Returns/Raises docstrings
- **Professional error handling** with custom exception hierarchy
- **Performance optimizations** for large canvas support

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Submit a pull request

### Testing
The application includes comprehensive validation and error handling. To test:
1. Try various canvas sizes and drawing operations
2. Test file save/load with different projects
3. Verify keyboard shortcuts work as expected
4. Test zoom functionality and performance

## Technical Details

### Performance Features
- Sparse pixel storage (only non-default colors stored)
- Dirty region rendering (only updated areas redrawn)
- Cached UI elements for smooth interaction
- Memory-efficient flood fill algorithm

### Cross-Platform Support
- Works on Windows, macOS, and Linux
- Uses native Qt rendering for platform consistency
- Follows platform conventions for keyboard shortcuts
- Professional appearance on all operating systems

## License

This project is open source. The application uses MIT-licensed Phosphor Icons for the tool interface.

## Support

For issues or questions:
- Check the GitHub Issues page
- Review the comprehensive error messages in the application
- Refer to the built-in status bar for operation feedback

---

Created with modern Python development practices and professional software architecture patterns.