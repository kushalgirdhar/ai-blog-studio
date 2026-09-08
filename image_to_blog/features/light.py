"""Lighting, contrast, and color temperature metrics."""

from typing import Dict, List, Tuple
import cv2
import numpy as np


def brightness_contrast(cv_image: np.ndarray) -> Dict[str, float]:
    """
    Compute mean brightness and standard deviation contrast from grayscale image.
    
    Returns:
        {"mean_brightness": float, "std_contrast": float}
    """
    if cv_image is None or cv_image.size == 0:
        return {"mean_brightness": 128.0, "std_contrast": 50.0}

    gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
    mean_val = float(np.mean(gray))
    std_val = float(np.std(gray))

    return {
        "mean_brightness": round(mean_val, 2),
        "std_contrast": round(std_val, 2),
    }


def warmth_score(rgb_list: List[Tuple[int, int, int]]) -> float:
    """
    Compute warmth score from dominant RGB colors.
    Score ranges from -1.0 (very cool/blue) to +1.0 (very warm/red-yellow).
    """
    if not rgb_list:
        return 0.0

    scores = []
    for r, g, b in rgb_list:
        # Red is warm (+), Blue is cool (-), Green is neutral
        total = float(r + g + b)
        if total < 1e-3:
            scores.append(0.0)
        else:
            diff = (r - b) / total
            scores.append(diff)

    mean_warmth = float(np.mean(scores))
    # Normalize gently to [-1.0, 1.0]
    normalized = float(np.clip(mean_warmth * 2.5, -1.0, 1.0))
    return round(normalized, 3)

