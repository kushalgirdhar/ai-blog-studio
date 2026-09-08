"""Composition, aspect ratio, focal point, and visual complexity analysis."""

from typing import Dict, Any
import cv2
import numpy as np
from PIL import Image
from image_to_blog.config import THRESHOLDS


def orientation(pil_image: Image.Image) -> str:
    """Determine image orientation: landscape, portrait, or square."""
    w, h = pil_image.size
    ratio = w / float(h)
    if ratio > 1.15:
        return "landscape"
    elif ratio < 0.87:
        return "portrait"
    return "square"


def focal_region(cv_image: np.ndarray) -> str:
    """
    Divide image into a 3x3 grid and find the region with highest visual detail (edge concentration).
    
    Returns one of:
        'center', 'top-left', 'top-center', 'top-right',
        'middle-left', 'middle-right', 'bottom-left',
        'bottom-center', 'bottom-right'
    """
    if cv_image is None or cv_image.size == 0:
        return "center"

    gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape

    if h < 6 or w < 6:
        return "center"

    # Edge map
    edges = cv2.Canny(gray, 50, 150)

    cell_h = h // 3
    cell_w = w // 3

    labels = [
        ["top-left", "top-center", "top-right"],
        ["middle-left", "center", "middle-right"],
        ["bottom-left", "bottom-center", "bottom-right"],
    ]

    max_count = -1
    best_region = "center"

    for r in range(3):
        for c in range(3):
            r_start = r * cell_h
            r_end = h if r == 2 else (r + 1) * cell_h
            c_start = c * cell_w
            c_end = w if c == 2 else (c + 1) * cell_w

            cell = edges[r_start:r_end, c_start:c_end]
            count = int(np.count_nonzero(cell))

            # Prioritize center slightly if counts are close (center bias in photography)
            weighted_count = count * 1.15 if (r == 1 and c == 1) else count

            if weighted_count > max_count:
                max_count = weighted_count
                best_region = labels[r][c]

    return best_region


def busyness_label(edge_density_value: float) -> str:
    """Classify visual complexity into minimal, balanced, or busy."""
    t = THRESHOLDS["edge_density"]
    if edge_density_value < t["minimal"]:
        return "minimal"
    elif edge_density_value < t["balanced"]:
        return "balanced"
    return "busy"

