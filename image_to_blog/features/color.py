"""Dominant color extraction and color naming."""

from typing import List, Tuple
import cv2
import numpy as np
from image_to_blog.config import COLOR_PALETTE


def dominant_colors(cv_image: np.ndarray, k: int = 5) -> List[Tuple[int, int, int]]:
    """
    Extract top-k dominant colors using K-Means clustering.
    
    Args:
        cv_image: OpenCV BGR image array.
        k: Number of dominant color clusters.
        
    Returns:
        List of (R, G, B) integer tuples sorted by cluster size descending.
    """
    if cv_image is None or cv_image.size == 0:
        return [(128, 128, 128)]

    # Resize image to thumbnail for fast clustering
    h, w = cv_image.shape[:2]
    max_dim = 150
    if max(h, w) > max_dim:
        scale = max_dim / float(max(h, w))
        resized = cv2.resize(cv_image, (max(1, int(w * scale)), max(1, int(h * scale))), interpolation=cv2.INTER_AREA)
    else:
        resized = cv_image

    # Convert BGR to RGB
    rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
    pixels = rgb.reshape(-1, 3).astype(np.float32)

    # If pixel count is smaller than k, adjust k
    actual_k = min(k, len(pixels))
    if actual_k <= 0:
        return [(128, 128, 128)]

    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 0.2)
    flags = cv2.KMEANS_PP_CENTERS

    _, labels, centers = cv2.kmeans(pixels, actual_k, None, criteria, 5, flags)

    # Count frequencies of each cluster
    labels = labels.flatten()
    counts = np.bincount(labels, minlength=actual_k)
    sorted_indices = np.argsort(counts)[::-1]

    colors: List[Tuple[int, int, int]] = []
    for idx in sorted_indices:
        c = centers[idx]
        colors.append((int(np.clip(c[0], 0, 255)), int(np.clip(c[1], 0, 255)), int(np.clip(c[2], 0, 255))))

    return colors


def nearest_color_name(rgb: Tuple[int, int, int]) -> str:
    """Find the closest named color using weighted Euclidean distance in RGB."""
    r, g, b = rgb
    best_name = "gray"
    best_dist = float("inf")

    for name, (cr, cg, cb) in COLOR_PALETTE.items():
        # Weighted RGB distance approximation for human perception
        # rmean = (r + cr) / 2
        # d = sqrt( (2 + rmean/256)*dr^2 + 4*dg^2 + (2 + (255-rmean)/256)*db^2 )
        dr = r - cr
        dg = g - cg
        db = b - cb
        rmean = (r + cr) / 2.0
        dist = (2.0 + rmean / 256.0) * (dr ** 2) + 4.0 * (dg ** 2) + (2.0 + (255.0 - rmean) / 256.0) * (db ** 2)
        if dist < best_dist:
            best_dist = dist
            best_name = name

    return best_name


def name_colors(rgb_list: List[Tuple[int, int, int]]) -> List[str]:
    """
    Map a list of RGB colors to descriptive names, removing consecutive duplicates.
    """
    names = []
    seen = set()
    for rgb in rgb_list:
        name = nearest_color_name(rgb)
        if name not in seen:
            seen.add(name)
            names.append(name)
    
    if not names:
        names.append("neutral gray")
        
    return names

