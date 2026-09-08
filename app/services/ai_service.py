import os
import json
import logging
from typing import Dict, Any, Optional

from image_to_blog.api import generate_blog_text
from db_copyright_checker import check_blog_draft_copyright

logger = logging.getLogger(__name__)


def generate_blog_from_image(
    image_path: str, extra_corpus: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Generate blog post content (title, short_description, description) from an uploaded image,
    and run a local copyright / duplication check against reference docs and existing posts.
    """
    try:
        # Generate blog content using the image_to_blog rule-based engine
        blog_data = generate_blog_text(image_path)
    except Exception as e:
        logger.exception(f"Rule-based image-to-blog generation failed for {image_path}: {e}")
        blog_data = {
            "title": "Visual Impressions and Composition",
            "short_description": "An analysis of dominant colors, exposure, and composition.",
            "description": "A study in color palette, tonal balance, and visual structure derived from the uploaded image.",
        }

    # Run local copyright / duplication check
    try:
        copyright_report = check_blog_draft_copyright(
            title=blog_data.get("title", ""),
            short_description=blog_data.get("short_description", ""),
            description=blog_data.get("description", ""),
            extra_corpus=extra_corpus,
        )
        blog_data["copyright_check"] = copyright_report
    except Exception as e:
        logger.exception(f"Copyright check failed: {e}")
        blog_data["copyright_check"] = {
            "is_flagged": False,
            "summary_message": "Copyright check could not be completed.",
            "matched_phrases": [],
            "highlighted_fields": {
                "title": blog_data.get("title", ""),
                "short_description": blog_data.get("short_description", ""),
                "description": blog_data.get("description", ""),
            },
        }

    return blog_data


if __name__ == "__main__":
    image_path = input("Enter image path: ").strip()
    blog = generate_blog_from_image(image_path)
    print("\nGenerated Blog with Copyright Check:\n")
    print(json.dumps(blog, indent=4, ensure_ascii=False))

