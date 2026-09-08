"""Pipeline orchestrator: Ingestion -> Features -> Tracery Grammar Generation."""

from typing import Dict, Any, Union
from image_to_blog.ingestion import load_image
from image_to_blog.features.color import dominant_colors, name_colors
from image_to_blog.features.light import brightness_contrast, warmth_score
from image_to_blog.features.texture import sharpness_score, edge_density
from image_to_blog.features.composition import orientation, focal_region, busyness_label
from image_to_blog.features.metadata import extract_exif
from image_to_blog.features.text_ocr import extract_text
from image_to_blog.tracery_generator import generate_blog_text_tracery


def build_feature_dict(image_input: Union[str, bytes, Any]) -> Dict[str, Any]:
    """
    Run ingestion and all feature extractors over the image.
    """
    pil_img, cv_bgr = load_image(image_input)

    # Color
    dom_colors = dominant_colors(cv_bgr, k=5)
    color_names = name_colors(dom_colors)

    # Light & Temperature
    light_stats = brightness_contrast(cv_bgr)
    warmth = warmth_score(dom_colors)

    # Texture & Detail
    sharpness = sharpness_score(cv_bgr)
    edges = edge_density(cv_bgr)

    # Composition
    orient = orientation(pil_img)
    focal = focal_region(cv_bgr)
    busyness = busyness_label(edges)

    # Metadata & OCR
    exif = extract_exif(pil_img)
    ocr = extract_text(pil_img)

    return {
        "dominant_colors_rgb": dom_colors,
        "named_colors": color_names,
        "dominant_colors": color_names,
        "mean_brightness": light_stats["mean_brightness"],
        "std_contrast": light_stats["std_contrast"],
        "warmth_score": warmth,
        "sharpness_score": sharpness,
        "laplacian_variance": sharpness,
        "edge_density": edges,
        "orientation": orient,
        "focal_region": focal,
        "busyness_label": busyness,
        "exif": exif,
        "ocr_text": ocr,
        "image_size": pil_img.size,
    }


def generate_blog(image_input: Union[str, bytes, Any], seed: Union[int, None] = None) -> Dict[str, str]:
    """
    Full end-to-end generator pipeline using Tracery grammar generation.
    """
    features = build_feature_dict(image_input)
    return generate_blog_text_tracery(features)
