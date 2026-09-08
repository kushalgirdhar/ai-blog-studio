"""
Tracery grammar-based text generator for image-to-blog content.
Generates title, short description, and long description using recursive Tracery grammar expansion.
"""

from typing import Dict, Any, Optional
import tracery
from tracery.modifiers import base_english


def brightness_bucket(v: float) -> str:
    """Classify brightness value into dark, medium, or bright."""
    return "dark" if v < 85 else "medium" if v < 170 else "bright"


def warmth_bucket(v: float) -> str:
    """Classify warmth score into warm or cool."""
    return "warm" if v >= 0 else "cool"


def sharpness_bucket(v: float) -> str:
    """Classify sharpness score into sharp or soft."""
    return "sharp" if v > 100 else "soft"


def composition_bucket(v: float) -> str:
    """Classify edge density into minimal, balanced, or busy."""
    return "minimal" if v < 0.05 else "balanced" if v < 0.15 else "busy"


def build_grammar(bucket_values: Dict[str, str], features: Dict[str, Any]) -> tracery.Grammar:
    """
    Build recursive Tracery grammar rules using extracted buckets and feature parameters.
    """
    b = bucket_values.get("brightness", "medium")
    w = bucket_values.get("warmth", "cool")
    s = bucket_values.get("sharpness", "sharp")
    c = bucket_values.get("composition", "balanced")

    mood_options = {
        "dark": ["moody", "low-key", "shadow-rich", "contemplative", "enigmatic", "dramatic"],
        "medium": ["balanced", "even-toned", "natural", "harmonious", "distinctive", "classic"],
        "bright": ["bright", "airy", "luminous", "radiant", "vibrant", "spirited"],
    }.get(b, ["balanced", "natural"])

    warmth_options = {
        "cool": ["cool-toned", "crisp and cool", "calm with cool undertones", "serene cool-hued"],
        "warm": ["warm-toned", "golden", "sun-warmed", "cozy with warm undertones", "amber-infused"],
    }.get(w, ["neutral-toned", "naturally balanced"])

    sharp_options = {
        "soft": ["soft-focused", "dreamy", "gently diffused", "smoothly articulated"],
        "sharp": ["crisp", "sharply detailed", "razor-sharp", "clearly articulated"],
    }.get(s, ["crisp", "well-defined"])

    comp_options = {
        "minimal": [
            "a minimal composition",
            "an uncluttered frame",
            "a clean, spacious layout",
            "generous negative space",
        ],
        "balanced": [
            "a balanced composition",
            "a well-composed frame",
            "a harmonious compositional rhythm",
            "an orderly visual flow",
        ],
        "busy": [
            "a busy, detail-rich composition",
            "a visually dense frame",
            "an intricate and layered structure",
            "a dynamic, information-rich arrangement",
        ],
    }.get(c, ["a balanced composition", "a well-composed frame"])

    dom_colors = features.get("dominant_colors", features.get("named_colors", ["slate gray", "charcoal"]))
    if not dom_colors:
        dom_colors = ["slate gray", "charcoal"]

    color1 = dom_colors[0]
    color2 = dom_colors[1] if len(dom_colors) > 1 else "slate gray"
    color3 = dom_colors[2] if len(dom_colors) > 2 else "silver"

    orientation = features.get("orientation", "landscape")
    focal_region = features.get("focal_region", "center")

    focal_mapping = {
        "center": "focused at the center",
        "top-left": "anchored toward the upper-left quadrant",
        "top-center": "weighted toward the upper edge",
        "top-right": "anchored toward the upper-right corner",
        "middle-left": "aligned along the left section",
        "middle-right": "aligned along the right section",
        "bottom-left": "grounded in the lower-left section",
        "bottom-center": "grounded along the bottom foreground",
        "bottom-right": "grounded in the lower-right section",
    }
    focal_desc = focal_mapping.get(focal_region, "distributed across the frame")

    rules = {
        "mood": mood_options,
        "warmth": warmth_options,
        "sharpness": sharp_options,
        "composition": comp_options,
        "color1": [color1],
        "color2": [color2],
        "color3": [color3],
        "orientation": [orientation],
        "focal": [focal_desc],

        # Titles
        "title": [
            "#mood.capitalize# #color1.capitalize# & #color2.capitalize# Moments",
            "#mood.capitalize# #orientation.capitalize# Study in #color1.capitalize#",
            "Harmony of #color1.capitalize# and #color2.capitalize# Tones",
            "#mood.capitalize# Perspectives: #color1.capitalize# and #color2.capitalize#",
            "Exploration in #color1.capitalize#, #color2.capitalize#, and #color3.capitalize#",
        ],

        # Short Descriptions
        "short_description": [
            "#mood.a.capitalize# #color1# #orientation# scene, #warmth# with #sharpness# detail.",
            "#mood.a.capitalize# #orientation# visual piece featuring dominant #color1# and #color2# tones within #composition#.",
            "Featuring #warmth# highlights and #sharpness# textures, this #orientation# composition balances #color1# with #color2# accents.",
        ],

        # Long Descriptions
        "long_intro": [
            "This #orientation# visual piece creates #mood.a# ambiance, centered around a palette of #color1#, #color2#, and #color3#.",
            "Centered on #color1# and #color2# tones, this #orientation# composition presents #mood.a# atmosphere throughout.",
            "Anchored by rich #color1# and accented by #color2#, the #orientation# frame establishes #mood.a# visual narrative.",
        ],
        "long_body": [
            "The image is #sharpness# and #warmth#, set within #composition#.",
            "With #sharpness# fidelity and #warmth# nuances, visual energy is #focal#.",
            "Textural elements remain #sharpness#, while the lighting feels #warmth# within #composition#.",
        ],
        "long_conclusion": [
            "The overall visual balance highlights the interplay between light and form.",
            "The resulting aesthetic provides clean visual rhythm and tonal cohesion.",
            "The combination of palette harmony and framing delivers a distinct artistic presence.",
        ],
        "long_description": [
            "#long_intro# #long_body# #long_conclusion#",
        ],
    }

    grammar = tracery.Grammar(rules)
    grammar.add_modifiers(base_english)
    return grammar


def generate_blog_text_tracery(features: Dict[str, Any]) -> Dict[str, str]:
    """
    Generate blog text dictionary from image features using Tracery grammar.
    """
    mean_b = features.get("mean_brightness", 128.0)
    warmth_val = features.get("warmth_score", 0.0)
    sharpness_val = features.get("laplacian_variance", features.get("sharpness_score", 150.0))
    edge_val = features.get("edge_density", 0.08)

    bucket_values = {
        "brightness": brightness_bucket(mean_b),
        "warmth": warmth_bucket(warmth_val),
        "sharpness": sharpness_bucket(sharpness_val),
        "composition": composition_bucket(edge_val),
    }

    grammar = build_grammar(bucket_values, features)

    title = grammar.flatten("#title#")
    short_desc = grammar.flatten("#short_description#")
    long_desc = grammar.flatten("#long_description#")

    # Append OCR text if detected
    ocr_text = features.get("ocr_text", "").strip()
    if ocr_text:
        long_desc += f' Visible text in the image reads: "{ocr_text}".'

    # Append EXIF camera info if available
    exif = features.get("exif", {})
    if exif:
        camera = f"{exif.get('make', '')} {exif.get('model', '')}".strip()
        details = []
        if camera:
            details.append(f"shot with {camera}")
        if exif.get("focal_length"):
            details.append(f"{exif['focal_length']}mm")
        if exif.get("f_number"):
            details.append(f"f/{exif['f_number']}")
        if exif.get("iso"):
            details.append(f"ISO {exif['iso']}")
        if details:
            long_desc += f" Camera metadata indicates settings {', '.join(details)}."

    return {
        "title": title.strip(),
        "short_description": short_desc.strip(),
        "description": long_desc.strip(),
        "long_description": long_desc.strip(),
    }

