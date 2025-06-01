#!/usr/bin/env python3
"""
Setup script for Pixel Drawing application.
"""

from setuptools import setup, find_packages
import os

# Read the contents of README file for long_description
def read_readme():
    """Read README.md file for package description."""
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    try:
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        # Fallback description if README.md doesn't exist
        return "A cross-platform pixel art application for creating retro game assets."

long_description = read_readme()

setup(
    name="pixel-drawing",
    version="1.0.0",
    description="A cross-platform pixel art application for creating retro game assets",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Pixel Drawing Team",
    python_requires=">=3.7",
    install_requires=[
        "PyQt6>=6.4.0",
        "Pillow>=9.0.0",
    ],
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "pixel-drawing=pixel_drawing.app:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Topic :: Multimedia :: Graphics :: Editors",
        "Topic :: Games/Entertainment",
    ],
)