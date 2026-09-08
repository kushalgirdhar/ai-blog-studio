"""Comprehensive unit and integration tests for image_to_blog generator."""

import io
import unittest
import numpy as np
from PIL import Image, ImageDraw

from image_to_blog.ingestion import load_image
from image_to_blog.features.color import dominant_colors, name_colors, nearest_color_name
from image_to_blog.features.light import brightness_contrast, warmth_score
from image_to_blog.features.texture import sharpness_score, edge_density
from image_to_blog.features.composition import orientation, focal_region, busyness_label
from image_to_blog.features.metadata import extract_exif
from image_to_blog.features.text_ocr import extract_text
from image_to_blog.phrasing import build_phrases
from image_to_blog.generator import build_feature_dict, generate_blog
from image_to_blog.api import generate_blog_text


class TestImageToBlog(unittest.TestCase):

    def setUp(self):
        # Create standard test images in memory
        # 1. RGB Landscape Image
        self.rgb_img = Image.new("RGB", (300, 200), color=(50, 100, 150))
        d = ImageDraw.Draw(self.rgb_img)
        d.rectangle([(50, 50), (150, 150)], fill=(200, 50, 50))
        self.rgb_io = io.BytesIO()
        self.rgb_img.save(self.rgb_io, format="PNG")
        self.rgb_io.seek(0)

        # 2. Text Image for OCR
        self.text_img = Image.new("RGB", (400, 100), color=(255, 255, 255))
        d2 = ImageDraw.Draw(self.text_img)
        d2.text((20, 30), "Artificial Intelligence", fill=(0, 0, 0))
        self.text_io = io.BytesIO()
        self.text_img.save(self.text_io, format="PNG")
        self.text_io.seek(0)

    def test_ingestion_valid_rgb(self):
        pil_img, cv_bgr = load_image(self.rgb_io)
        self.assertIsInstance(pil_img, Image.Image)
        self.assertEqual(pil_img.mode, "RGB")
        self.assertIsInstance(cv_bgr, np.ndarray)
        self.assertEqual(cv_bgr.ndim, 3)
        self.assertEqual(cv_bgr.shape[2], 3)

    def test_ingestion_grayscale_and_rgba(self):
        # Grayscale
        gray = Image.new("L", (100, 100), color=128)
        gray_io = io.BytesIO()
        gray.save(gray_io, format="PNG")
        gray_io.seek(0)
        pil_g, cv_g = load_image(gray_io)
        self.assertEqual(pil_g.mode, "RGB")
        self.assertEqual(cv_g.shape, (100, 100, 3))

        # RGBA with transparency
        rgba = Image.new("RGBA", (100, 100), color=(255, 0, 0, 128))
        rgba_io = io.BytesIO()
        rgba.save(rgba_io, format="PNG")
        rgba_io.seek(0)
        pil_a, cv_a = load_image(rgba_io)
        self.assertEqual(pil_a.mode, "RGB")
        self.assertEqual(cv_a.shape, (100, 100, 3))

    def test_ingestion_corrupted(self):
        corrupt_io = io.BytesIO(b"not an image data stream")
        with self.assertRaises(ValueError):
            load_image(corrupt_io)

    def test_ingestion_tiny_image(self):
        tiny = Image.new("RGB", (5, 5), color=(255, 255, 0))
        tiny_io = io.BytesIO()
        tiny.save(tiny_io, format="PNG")
        tiny_io.seek(0)
        pil_t, cv_t = load_image(tiny_io)
        self.assertEqual(pil_t.size, (5, 5))

    def test_color_features(self):
        _, cv_bgr = load_image(self.rgb_io)
        dom = dominant_colors(cv_bgr, k=3)
        self.assertIsInstance(dom, list)
        self.assertGreaterEqual(len(dom), 1)
        for c in dom:
            self.assertEqual(len(c), 3)

        names = name_colors(dom)
        self.assertIsInstance(names, list)
        self.assertGreater(len(names), 0)
        for n in names:
            self.assertIsInstance(n, str)

    def test_light_features(self):
        _, cv_bgr = load_image(self.rgb_io)
        stats = brightness_contrast(cv_bgr)
        self.assertIn("mean_brightness", stats)
        self.assertIn("std_contrast", stats)
        self.assertGreaterEqual(stats["mean_brightness"], 0)
        self.assertLessEqual(stats["mean_brightness"], 255)

        warmth = warmth_score([(255, 0, 0), (200, 50, 0)])
        self.assertGreater(warmth, 0.0)

        cool = warmth_score([(0, 50, 255), (20, 40, 200)])
        self.assertLess(cool, 0.0)

    def test_texture_features(self):
        _, cv_bgr = load_image(self.rgb_io)
        sharp = sharpness_score(cv_bgr)
        self.assertIsInstance(sharp, float)
        self.assertGreaterEqual(sharp, 0.0)

        density = edge_density(cv_bgr)
        self.assertIsInstance(density, float)
        self.assertGreaterEqual(density, 0.0)
        self.assertLessEqual(density, 1.0)

    def test_composition_features(self):
        pil_img, cv_bgr = load_image(self.rgb_io)
        orient = orientation(pil_img)
        self.assertEqual(orient, "landscape")

        focal = focal_region(cv_bgr)
        self.assertIsInstance(focal, str)

        b_label = busyness_label(0.01)
        self.assertEqual(b_label, "minimal")
        b_label_busy = busyness_label(0.20)
        self.assertEqual(b_label_busy, "busy")

    def test_metadata_and_ocr(self):
        pil_img, _ = load_image(self.rgb_io)
        exif = extract_exif(pil_img)
        self.assertIsInstance(exif, dict)

        pil_text, _ = load_image(self.text_io)
        ocr = extract_text(pil_text)
        self.assertIsInstance(ocr, str)
        if ocr:
            self.assertTrue("Artificial" in ocr or "Intel" in ocr)

    def test_end_to_end_generation(self):
        self.rgb_io.seek(0)
        result = generate_blog_text(self.rgb_io)
        self.assertIn("title", result)
        self.assertIn("short_description", result)
        self.assertIn("description", result)
        self.assertTrue(len(result["title"]) > 0)
        self.assertTrue(len(result["short_description"]) > 0)
        self.assertTrue(len(result["description"]) > 0)


if __name__ == "__main__":
    unittest.main()
