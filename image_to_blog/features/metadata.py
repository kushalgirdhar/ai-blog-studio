"""EXIF metadata extraction."""

from typing import Dict, Any
from PIL import Image, ExifTags


def extract_exif(pil_image: Image.Image) -> Dict[str, Any]:
    """
    Extract readable EXIF camera and shooting metadata from a PIL Image.
    
    Returns:
        Dict containing available fields such as:
        {
            "make": str,
            "model": str,
            "datetime": str,
            "exposure_time": str,
            "f_number": float,
            "iso": int,
            "focal_length": float,
        }
    """
    exif_data: Dict[str, Any] = {}
    try:
        raw_exif = pil_image.getexif()
        if not raw_exif:
            return exif_data

        # Map tag IDs to human-readable names
        for tag_id, value in raw_exif.items():
            tag_name = ExifTags.TAGS.get(tag_id, str(tag_id))
            if tag_name == "Make" and isinstance(value, str):
                exif_data["make"] = value.strip().replace("\x00", "")
            elif tag_name == "Model" and isinstance(value, str):
                exif_data["model"] = value.strip().replace("\x00", "")
            elif tag_name == "DateTime" and isinstance(value, str):
                exif_data["datetime"] = value.strip().replace("\x00", "")
            elif tag_name == "ExposureTime":
                exif_data["exposure_time"] = f"{value}s" if isinstance(value, (int, float, str)) else str(value)
            elif tag_name == "FNumber":
                try:
                    exif_data["f_number"] = float(value)
                except Exception:
                    pass
            elif tag_name == "ISOSpeedRatings":
                try:
                    exif_data["iso"] = int(value)
                except Exception:
                    pass
            elif tag_name == "FocalLength":
                try:
                    exif_data["focal_length"] = float(value)
                except Exception:
                    pass

    except Exception:
        # Silently fail on unreadable or corrupt EXIF
        return {}

    return exif_data

