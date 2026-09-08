"""Translation of numeric and categorical image features into natural phrasing."""

import random
from typing import Dict, List, Any, Optional
from image_to_blog.config import THRESHOLDS, PHRASE_BANKS


def get_random_choice(choices: List[str], rng: Optional[random.Random] = None) -> str:
    """Safely select an element from list."""
    if not choices:
        return ""
    if rng is not None:
        return rng.choice(choices)
    return random.choice(choices)


def brightness_phrase(mean_brightness: float, rng: Optional[random.Random] = None) -> str:
    """Return descriptive lighting phrase based on mean brightness."""
    t = THRESHOLDS["brightness"]
    if mean_brightness < t["dark"]:
        bucket = "dark"
    elif mean_brightness < t["medium_dark"]:
        bucket = "medium_dark"
    elif mean_brightness < t["balanced"]:
        bucket = "balanced"
    elif mean_brightness < t["bright"]:
        bucket = "bright"
    else:
        bucket = "high_key"
    return get_random_choice(PHRASE_BANKS["brightness"][bucket], rng)


def contrast_phrase(std_contrast: float, rng: Optional[random.Random] = None) -> str:
    """Return contrast description."""
    t = THRESHOLDS["contrast"]
    if std_contrast < t["low"]:
        bucket = "low"
    elif std_contrast < t["moderate"]:
        bucket = "moderate"
    else:
        bucket = "high"
    return get_random_choice(PHRASE_BANKS["contrast"][bucket], rng)


def warmth_phrase(warmth_val: float, rng: Optional[random.Random] = None) -> str:
    """Return color temperature description."""
    t = THRESHOLDS["warmth"]
    if warmth_val < t["cool"]:
        bucket = "cool"
    elif warmth_val > t["warm"]:
        bucket = "warm"
    else:
        bucket = "neutral"
    return get_random_choice(PHRASE_BANKS["warmth"][bucket], rng)


def sharpness_phrase(sharpness_val: float, rng: Optional[random.Random] = None) -> str:
    """Return texture and edge clarity description."""
    t = THRESHOLDS["sharpness"]
    if sharpness_val < t["soft"]:
        bucket = "soft"
    elif sharpness_val < t["moderate"]:
        bucket = "moderate"
    else:
        bucket = "sharp"
    return get_random_choice(PHRASE_BANKS["sharpness"][bucket], rng)


def busyness_phrase(label: str, rng: Optional[random.Random] = None) -> str:
    """Return visual complexity description."""
    bucket = label if label in PHRASE_BANKS["busyness"] else "balanced"
    return get_random_choice(PHRASE_BANKS["busyness"][bucket], rng)


def mood_word(mean_brightness: float, warmth_val: float, std_contrast: float, rng: Optional[random.Random] = None) -> str:
    """Synthesize lighting, temperature, and contrast into a primary mood word."""
    if mean_brightness < 75 and std_contrast > 45:
        category = "mysterious_dark"
    elif warmth_val > 0.15:
        category = "warm_inviting"
    elif warmth_val < -0.15:
        category = "cool_serene"
    elif std_contrast > 60:
        category = "vibrant_energetic"
    elif mean_brightness > 160:
        category = "clean_minimal"
    else:
        category = "balanced_classic"

    return get_random_choice(PHRASE_BANKS["mood"][category], rng)


def format_palette_names(color_names: List[str]) -> Dict[str, str]:
    """Provide formatted combinations of color names."""
    if not color_names:
        return {
            "primary": "neutral gray",
            "secondary": "charcoal",
            "accent": "slate",
            "all_list": "neutral tones",
            "pair": "neutral tones",
        }

    c1 = color_names[0]
    c2 = color_names[1] if len(color_names) > 1 else "slate gray"
    c3 = color_names[2] if len(color_names) > 2 else ""

    if len(color_names) == 1:
        all_list = c1
        pair = c1
    elif len(color_names) == 2:
        all_list = f"{c1} and {c2}"
        pair = f"{c1} and {c2}"
    else:
        all_list = f"{c1}, {c2}, and {c3}" if c3 else f"{c1} and {c2}"
        pair = f"{c1} and {c2}"

    return {
        "primary": c1,
        "secondary": c2,
        "accent": c3,
        "all_list": all_list,
        "pair": pair,
    }


def format_focal_description(focal_region: str) -> str:
    """Natural description of focal region."""
    mapping = {
        "center": "centered in the composition",
        "top-left": "positioned toward the upper-left quadrant",
        "top-center": "anchored in the upper area",
        "top-right": "positioned toward the upper-right corner",
        "middle-left": "aligned along the left third",
        "middle-right": "aligned along the right third",
        "bottom-left": "situated in the lower-left section",
        "bottom-center": "grounded along the lower boundary",
        "bottom-right": "situated in the lower-right section",
    }
    return mapping.get(focal_region, "balanced across the frame")


def build_phrases(features: Dict[str, Any], seed: Optional[int] = None) -> Dict[str, Any]:
    """
    Compile all raw features into a comprehensive dictionary of descriptive phrases.
    """
    rng = random.Random(seed) if seed is not None else None

    mean_b = features.get("mean_brightness", 128.0)
    std_c = features.get("std_contrast", 50.0)
    warmth = features.get("warmth_score", 0.0)
    sharpness = features.get("sharpness_score", 200.0)
    busyness = features.get("busyness_label", "balanced")
    color_names = features.get("named_colors", ["slate gray", "silver"])
    focal = features.get("focal_region", "center")
    orientation_val = features.get("orientation", "landscape")
    exif = features.get("exif", {})
    ocr = features.get("ocr_text", "")

    pal = format_palette_names(color_names)

    # Build EXIF summary sentence if metadata exists
    exif_sentence = ""
    if exif:
        camera = f"{exif.get('make', '')} {exif.get('model', '')}".strip()
        details = []
        if camera:
            details.append(f"captured on {camera}")
        if exif.get("focal_length"):
            details.append(f"at {exif['focal_length']}mm")
        if exif.get("f_number"):
            details.append(f"f/{exif['f_number']}")
        if exif.get("iso"):
            details.append(f"ISO {exif['iso']}")
        if exif.get("exposure_time"):
            details.append(f"{exif['exposure_time']} exposure")
        if details:
            exif_sentence = f"Technical metadata reflects settings {', '.join(details)}."

    ocr_sentence = ""
    if ocr:
        ocr_sentence = f'The visual composition incorporates the text phrase "{ocr}".'

    return {
        "mood": mood_word(mean_b, warmth, std_c, rng),
        "primary_color": pal["primary"],
        "secondary_color": pal["secondary"],
        "accent_color": pal["accent"],
        "palette_pair": pal["pair"],
        "palette_list": pal["all_list"],
        "brightness_desc": brightness_phrase(mean_b, rng),
        "contrast_desc": contrast_phrase(std_c, rng),
        "warmth_desc": warmth_phrase(warmth, rng),
        "sharpness_desc": sharpness_phrase(sharpness, rng),
        "busyness_desc": busyness_phrase(busyness, rng),
        "orientation": orientation_val,
        "focal_region": focal,
        "focal_desc": format_focal_description(focal),
        "exif_sentence": exif_sentence,
        "ocr_sentence": ocr_sentence,
        "has_ocr": bool(ocr),
        "has_exif": bool(exif_sentence),
    }

