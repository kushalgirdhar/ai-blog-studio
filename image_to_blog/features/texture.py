"""Texture, sharpness, and edge complexity analysis."""

import cv2
import numpy as np


def sharpness_score(cv_image: np.ndarray) -> float:
    """
    Compute image sharpness via variance of the Laplacian filter.
    Higher values indicate crisp focus and fine details.
    """
    if cv_image is None or cv_image.size == 0:
        return 0.0

    gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    variance = float(laplacian.var())
    return round(variance, 2)


def edge_density(cv_image: np.ndarray) -> float:
    """
    Compute edge pixel density using Canny edge detection.
    Returns ratio of edge pixels to total pixels (0.0 to 1.0).
    """
    if cv_image is None or cv_image.size == 0:
        return 0.0

    gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
    
    # Auto-adjust Canny thresholds based on image median intensity
    med = np.median(gray)
    lower = int(max(0, (1.0 - 0.33) * med))
    upper = int(min(255, (1.0 + 0.33) * med))
    if lower == upper:
        lower, upper = 50, 150

    edges = cv2.Canny(gray, lower, upper)
    total_pixels = float(edges.shape[0] * edges.shape[1])
    if total_pixels == 0:
        return 0.0

    edge_count = float(np.count_nonzero(edges))
    density = edge_count / total_pixels
    return round(density, 4)

