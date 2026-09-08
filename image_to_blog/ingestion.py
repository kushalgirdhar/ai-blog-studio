"""Image ingestion, normalization, and validation."""

import io
from typing import Tuple, Union
import numpy as np
from PIL import Image, ImageOps


def load_image(path_or_file: Union[str, bytes, io.BytesIO]) -> Tuple[Image.Image, np.ndarray]:
    """
    Load an image from file path, bytes, or file-like object.
    
    Returns:
        tuple (pil_image_rgb, cv2_bgr_array):
            - pil_image_rgb: PIL.Image in RGB mode with EXIF intact where possible
            - cv2_bgr_array: NumPy array in BGR format suitable for OpenCV operations.
            
    Raises:
        ValueError: If the image cannot be read, decoded, or is corrupted.
    """
    try:
        if isinstance(path_or_file, bytes):
            image_stream = io.BytesIO(path_or_file)
        elif hasattr(path_or_file, "read"):
            # File-like object
            content = path_or_file.read()
            if isinstance(content, str):
                content = content.encode("utf-8")
            image_stream = io.BytesIO(content)
        else:
            with open(path_or_file, "rb") as f:
                image_stream = io.BytesIO(f.read())

        # Open with PIL
        pil_img = Image.open(image_stream)
        # Verify and force load pixels into memory
        pil_img.load()

        # Handle orientation tag from EXIF if present
        try:
            pil_img = ImageOps.exif_transpose(pil_img)
        except Exception:
            pass

        # Convert to RGB mode safely handling transparency, CMYK, Palette, Grayscale
        if pil_img.mode in ("RGBA", "LA") or (pil_img.mode == "P" and "transparency" in pil_img.info):
            # Composite over white background to avoid black background artifacts
            rgba = pil_img.convert("RGBA")
            background = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
            composite = Image.alpha_composite(background, rgba)
            pil_rgb = composite.convert("RGB")
        elif pil_img.mode != "RGB":
            pil_rgb = pil_img.convert("RGB")
        else:
            pil_rgb = pil_img.copy()

        # Build OpenCV BGR numpy array
        rgb_array = np.array(pil_rgb)
        if rgb_array.size == 0 or rgb_array.ndim != 3 or rgb_array.shape[2] != 3:
            raise ValueError("Invalid image dimensions decoded.")

        # RGB to BGR
        cv_bgr = rgb_array[:, :, ::-1].copy()

        return pil_rgb, cv_bgr

    except Exception as e:
        raise ValueError(f"Failed to load and process image: {e}") from e

