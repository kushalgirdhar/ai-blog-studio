"""Public API entrypoint for image-to-blog text generator."""

from typing import Dict, Any, Union, Optional
from image_to_blog.generator import generate_blog


def generate_blog_text(image_path_or_file: Union[str, bytes, Any], seed: Optional[int] = None) -> Dict[str, str]:
    """
    Generate blog draft dictionary {title, short_description, description} from an image.
    
    Args:
        image_path_or_file: File path string, image bytes, or file-like object.
        seed: Optional random seed for reproducible phrasing variations.
        
    Returns:
        Dict with keys:
            - 'title': str
            - 'short_description': str
            - 'description': str
    """
    return generate_blog(image_path_or_file, seed=seed)

