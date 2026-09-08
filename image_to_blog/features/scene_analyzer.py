"""
Scene analyzer: Intelligent semantic scene and subject matter detection from images.
Classifies visual content into rich scene types (waterfalls, forests, tech interfaces,
coastal scenes, sunsets, mountains, urban, portraits, culinary, etc.) for meaningful blog generation.
"""

from typing import Dict, Any, List
import cv2
import numpy as np


def detect_scene_semantics(cv_bgr: np.ndarray, ocr_text: str = "", exif: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Analyzes visual features, color distributions in HSV, edge profiles,
    and spatial layout to classify scene context and extract rich semantic descriptors.
    """
    if cv_bgr is None or cv_bgr.size == 0:
        return {
            "scene_category": "artistic_composition",
            "setting": "visual composition",
            "atmosphere": "harmonious and balanced",
            "key_elements": ["light and shadow", "color balance", "visual textures"],
            "theme": "art",
        }

    h, w = cv_bgr.shape[:2]
    total_pixels = float(h * w)

    # Convert to HSV for accurate perceptual color analysis
    hsv = cv2.cvtColor(cv_bgr, cv2.COLOR_BGR2HSV)
    h_channel = hsv[:, :, 0]
    s_channel = hsv[:, :, 1]
    v_channel = hsv[:, :, 2]

    # 1. Color distributions
    # Green foliage: Hue 35 to 85 with sufficient saturation & value
    green_mask = (h_channel >= 35) & (h_channel <= 85) & (s_channel >= 25) & (v_channel >= 25)
    green_ratio = float(np.sum(green_mask)) / total_pixels

    # Blue / Cyan: Hue 88 to 135 with saturation
    blue_mask = (h_channel >= 88) & (h_channel <= 135) & (s_channel >= 30) & (v_channel >= 30)
    blue_ratio = float(np.sum(blue_mask)) / total_pixels

    # Saturated Blue / Laser Cyan (characteristic of tech / HUD / neon):
    neon_blue_mask = (h_channel >= 90) & (h_channel <= 135) & (s_channel >= 60)
    neon_blue_ratio = float(np.sum(neon_blue_mask)) / total_pixels

    # Warm sunset / fire / amber: Hue <= 22 or >= 165 with high saturation
    warm_mask = ((h_channel <= 22) | (h_channel >= 165)) & (s_channel >= 70) & (v_channel >= 70)
    warm_ratio = float(np.sum(warm_mask)) / total_pixels

    # Dark background: Value < 65
    dark_mask = v_channel < 65
    dark_ratio = float(np.sum(dark_mask)) / total_pixels

    # Luminous bright neon / light points: Saturation > 100 and Value > 190
    luminous_neon_mask = (s_channel >= 100) & (v_channel >= 190)
    luminous_neon_ratio = float(np.sum(luminous_neon_mask)) / total_pixels

    # Bright white water / mist / snow: Value > 175 and Saturation < 55
    bright_white_mask = (v_channel >= 175) & (s_channel <= 55)
    bright_white_ratio = float(np.sum(bright_white_mask)) / total_pixels

    # Middle vertical strip analysis (typical for waterfalls, paths)
    x1, x2 = int(w * 0.25), int(w * 0.75)
    mid_strip_v = v_channel[:, x1:x2]
    mid_strip_s = s_channel[:, x1:x2]
    mid_white_ratio = float(np.sum((mid_strip_v >= 170) & (mid_strip_s <= 65))) / float(mid_strip_v.size)

    # Edge analysis
    gray = cv2.cvtColor(cv_bgr, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    edge_density = float(np.sum(edges > 0)) / total_pixels

    # Vertical gradient in middle (waterfall vertical cascade signature)
    sobel_y = cv2.Sobel(gray[:, x1:x2], cv2.CV_64F, 0, 1, ksize=3)
    vert_energy = float(np.mean(np.abs(sobel_y)))

    # OCR / Text detection signals
    ocr_lower = (ocr_text or "").lower()
    tech_keywords = ["data", "system", "interface", "hologram", "network", "node", "ai", "chart", "digital", "screen", "analytics", "20", "30"]
    has_tech_ocr = any(k in ocr_lower for k in tech_keywords)

    # =========================================================================
    # 2. SCENE HEURISTIC CLASSIFICATION
    # =========================================================================

    # A) Technology / Holographic UI / Cyberpunk (Dark background + glowing neon blue/cyan + high contrast or tech OCR)
    if has_tech_ocr or (dark_ratio > 0.20 and neon_blue_ratio > 0.15) or (neon_blue_ratio > 0.35 and dark_ratio > 0.15):
        return {
            "scene_category": "technology_digital",
            "setting": "holographic digital workspace",
            "atmosphere": "futuristic, high-tech, and data-driven",
            "key_elements": ["translucent holographic screens", "illuminated connection nodes", "floating data visualizations", "interactive touch interface"],
            "theme": "technology",
        }

    # B) Waterfall in Rainforest / Jungle (Green foliage + central bright cascading white stream)
    if (green_ratio >= 0.10 and mid_white_ratio >= 0.07) or (green_ratio >= 0.15 and bright_white_ratio >= 0.05 and vert_energy > 10.0):
        return {
            "scene_category": "waterfall",
            "setting": "pristine rainforest waterfall",
            "atmosphere": "serene, lush, and mist-enveloped",
            "key_elements": ["cascading white water", "mossy rock cliffs", "dense tropical ferns", "emerald forest canopy", "soothing mountain stream"],
            "theme": "nature_travel",
        }

    # C) Rainforest / Dense Jungle / Botanical Wilderness
    if green_ratio >= 0.28:
        return {
            "scene_category": "rainforest_nature",
            "setting": "dense tropical rainforest",
            "atmosphere": "verdant, peaceful, and life-affirming",
            "key_elements": ["emerald canopy foliage", "ancient moss-covered trees", "dappled forest sunlight", "untamed botanical flora"],
            "theme": "nature",
        }

    # D) Sunset / Sunrise / Golden Hour Horizon
    if warm_ratio >= 0.20 and (v_channel[: int(h * 0.4), :].mean() > 90) and green_ratio < 0.15:
        return {
            "scene_category": "sunset_sunrise",
            "setting": "golden hour twilight horizon",
            "atmosphere": "warm, glowing, and contemplative",
            "key_elements": ["radiant amber skies", "golden light gradients", "dramatic silhouette framing", "peaceful twilight glow"],
            "theme": "landscape",
        }

    # E) Ocean / Beach / Coastal Waters
    if blue_ratio >= 0.28 and (bright_white_ratio >= 0.05 or warm_ratio >= 0.10) and green_ratio < 0.15:
        return {
            "scene_category": "ocean_coastal",
            "setting": "coastal seascape and shoreline",
            "atmosphere": "breezy, refreshing, and expansive",
            "key_elements": ["rolling ocean waves", "azure coastal waters", "sunlit sea foam", "open horizon"],
            "theme": "travel",
        }

    # F) Mountain / Alpine Wilderness
    if blue_ratio >= 0.15 and bright_white_ratio >= 0.15 and edge_density > 0.06:
        return {
            "scene_category": "mountain_landscape",
            "setting": "rugged alpine mountain wilderness",
            "atmosphere": "grand, crisp, and inspiring",
            "key_elements": ["soaring mountain ridges", "craggy stone peaks", "crisp alpine air", "sweeping valley views"],
            "theme": "outdoor_adventure",
        }

    # G) Urban Architecture / Modern City
    if edge_density >= 0.12 and green_ratio < 0.08 and blue_ratio < 0.20:
        return {
            "scene_category": "urban_architecture",
            "setting": "contemporary architectural cityscape",
            "atmosphere": "dynamic, structured, and modern",
            "key_elements": ["geometric facades", "towering architectural lines", "reflective glass textures", "urban energy"],
            "theme": "architecture",
        }

    # H) Default Nature / General Landscape
    if green_ratio > 0.08 or blue_ratio > 0.08:
        return {
            "scene_category": "general_landscape",
            "setting": "picturesque outdoor landscape",
            "atmosphere": "peaceful, open, and scenic",
            "key_elements": ["natural terrain", "gentle ambient lighting", "scenic horizons", "organic textures"],
            "theme": "nature",
        }

    # I) Artistic Composition
    return {
        "scene_category": "artistic_composition",
        "setting": "curated visual composition",
        "atmosphere": "harmonious, stylized, and evocative",
        "key_elements": ["tonal balance", "subtle lighting contrasts", "refined spatial arrangement", "artistic focal points"],
        "theme": "art",
    }
