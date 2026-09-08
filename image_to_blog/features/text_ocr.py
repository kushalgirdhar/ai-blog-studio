"""Tesseract OCR embedded text extraction."""

import re
from PIL import Image

try:
    import pytesseract
    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False


def extract_text(pil_image: Image.Image) -> str:
    """
    Extract readable text from the image using Tesseract OCR.
    
    Returns:
        Cleaned text string, or empty string '' if no coherent text is detected.
    """
    if not PYTESSERACT_AVAILABLE or pil_image is None:
        return ""

    try:
        # Preprocess PIL image for better OCR: convert to grayscale
        gray = pil_image.convert("L")

        # Run tesseract
        raw_text = pytesseract.image_to_string(gray, timeout=5)
        if not raw_text:
            return ""

        # Clean text
        cleaned = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff]", " ", raw_text)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()

        # Reject pure garbage or single short tokens with no alphanumeric characters
        alphanumeric = re.findall(r"[A-Za-z0-9]", cleaned)
        if len(alphanumeric) < 3:
            return ""

        # Limit maximum length for summary
        if len(cleaned) > 200:
            cleaned = cleaned[:197].rsplit(" ", 1)[0] + "..."

        return cleaned

    except Exception:
        # Graceful fallback if tesseract binary is not accessible or fails
        return ""

