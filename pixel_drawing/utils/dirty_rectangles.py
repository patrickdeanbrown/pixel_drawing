"""Efficient dirty rectangle management for optimized canvas updates."""

from typing import Set, Tuple, List, Optional
from PyQt6.QtCore import QRect


class DirtyRegionManager:
    """Manages dirty rectangles for efficient canvas updates.
    
    Optimizes update performance by:
    - Merging overlapping dirty rectangles
    - Coalescing nearby regions to reduce update calls
    - Managing spatial locality for better cache performance
    """
    
    def __init__(self, pixel_size: int = 16, merge_threshold: int = 3):
        """Initialize dirty region manager.
        
        Args:
            pixel_size: Size of each pixel in screen coordinates
            merge_threshold: Maximum gap between regions to merge
        """
        self._pixel_size = pixel_size
        self._merge_threshold = merge_threshold
        self._dirty_pixels: Set[Tuple[int, int]] = set()
        self._dirty_rects: List[QRect] = []
    
    def mark_pixel_dirty(self, x: int, y: int) -> None:
        """Mark a single pixel as dirty.
        
        Args:
            x: Pixel X coordinate
            y: Pixel Y coordinate
        """
        self._dirty_pixels.add((x, y))
    
    def mark_pixels_dirty(self, pixels: Set[Tuple[int, int]]) -> None:
        """Mark multiple pixels as dirty efficiently.
        
        Args:
            pixels: Set of (x, y) pixel coordinates
        """
        self._dirty_pixels.update(pixels)
    
    def get_update_rectangles(self) -> List[QRect]:
        """Get optimized update rectangles for current dirty regions.
        
        Returns:
            List of QRect objects representing screen regions to update
        """
        if not self._dirty_pixels:
            return []
        
        # Convert pixels to screen rectangles and optimize
        self._optimize_dirty_regions()
        
        # Return copy and clear internal state
        result = self._dirty_rects.copy()
        self.clear()
        return result
    
    def _optimize_dirty_regions(self) -> None:
        """Convert dirty pixels to optimized rectangles."""
        if not self._dirty_pixels:
            return
        
        # Group pixels into clusters for efficient rectangle generation
        pixel_clusters = self._cluster_pixels()
        
        # Convert clusters to rectangles
        self._dirty_rects = []
        for cluster in pixel_clusters:
            rect = self._pixels_to_rect(cluster)
            self._dirty_rects.append(rect)
    
    def _cluster_pixels(self) -> List[Set[Tuple[int, int]]]:
        """Group nearby pixels into clusters for rectangle optimization.
        
        Returns:
            List of pixel clusters, each representing a connected region
        """
        unprocessed = self._dirty_pixels.copy()
        clusters = []
        
        while unprocessed:
            # Start new cluster with arbitrary pixel
            seed_pixel = unprocessed.pop()
            cluster = {seed_pixel}
            
            # Grow cluster by adding nearby pixels
            self._grow_cluster(cluster, unprocessed)
            clusters.append(cluster)
        
        return clusters
    
    def _grow_cluster(self, cluster: Set[Tuple[int, int]], 
                     unprocessed: Set[Tuple[int, int]]) -> None:
        """Grow a pixel cluster by adding nearby pixels.
        
        Args:
            cluster: Current cluster to grow
            unprocessed: Set of unprocessed pixels to consider
        """
        added_pixels = True
        while added_pixels:
            added_pixels = False
            to_add = set()
            
            for cluster_pixel in cluster:
                for unprocessed_pixel in unprocessed:
                    if self._pixels_nearby(cluster_pixel, unprocessed_pixel):
                        to_add.add(unprocessed_pixel)
                        added_pixels = True
            
            # Add nearby pixels to cluster
            cluster.update(to_add)
            unprocessed.difference_update(to_add)
    
    def _pixels_nearby(self, pixel1: Tuple[int, int], 
                      pixel2: Tuple[int, int]) -> bool:
        """Check if two pixels are close enough to merge.
        
        Args:
            pixel1: First pixel coordinates
            pixel2: Second pixel coordinates
            
        Returns:
            True if pixels should be in same cluster
        """
        x1, y1 = pixel1
        x2, y2 = pixel2
        return (abs(x1 - x2) <= self._merge_threshold and 
                abs(y1 - y2) <= self._merge_threshold)
    
    def _pixels_to_rect(self, pixels: Set[Tuple[int, int]]) -> QRect:
        """Convert a set of pixels to a bounding rectangle.
        
        Args:
            pixels: Set of pixel coordinates
            
        Returns:
            QRect representing the bounding rectangle in screen coordinates
        """
        if not pixels:
            return QRect()
        
        # Find bounding box
        min_x = min(x for x, y in pixels)
        max_x = max(x for x, y in pixels)
        min_y = min(y for x, y in pixels)
        max_y = max(y for x, y in pixels)
        
        # Convert to screen coordinates
        screen_x = min_x * self._pixel_size
        screen_y = min_y * self._pixel_size
        screen_width = (max_x - min_x + 1) * self._pixel_size
        screen_height = (max_y - min_y + 1) * self._pixel_size
        
        return QRect(screen_x, screen_y, screen_width, screen_height)
    
    def clear(self) -> None:
        """Clear all dirty regions."""
        self._dirty_pixels.clear()
        self._dirty_rects.clear()
    
    def is_empty(self) -> bool:
        """Check if there are no dirty regions."""
        return len(self._dirty_pixels) == 0