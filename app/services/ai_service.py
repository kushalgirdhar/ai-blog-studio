import os
import json
import logging
from typing import Dict, Any

from image_to_blog.api import generate_blog_text

logger = logging.getLogger(__name__)


def generate_blog_from_image(image_path: str) -> Dict[str, str]:
    """
    Generate blog post content (title, short_description, description) from an uploaded image.
    Uses classical computer vision, OCR, and rule-based generation (image_to_blog).
    """
    try:
        # Generate blog content using the image_to_blog rule-based engine
        return generate_blog_text(image_path)
    except Exception as e:
        logger.exception(f"Rule-based image-to-blog generation failed for {image_path}: {e}")
        # Return graceful default structure
        return {
            "title": "Visual Impressions and Composition",
            "short_description": "An analysis of dominant colors, exposure, and composition.",
            "description": "A study in color palette, tonal balance, and visual structure derived from the uploaded image.",
        }


if __name__ == "__main__":
    image_path = input("Enter image path: ").strip()
    blog = generate_blog_from_image(image_path)
    print("\nGenerated Blog:\n")
    print(json.dumps(blog, indent=4, ensure_ascii=False))
