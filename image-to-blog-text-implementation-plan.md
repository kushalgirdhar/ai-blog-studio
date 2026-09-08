# Implementation Plan: Rule-Based Image → Blog Text Generator

## Goal
Given an uploaded image, generate a `{title, short_description, long_description}` dict using only classical Python image-processing libraries — no API keys, no trained/pretrained AI models.

## Constraint reminder
No object/subject recognition. Everything below is derived purely from measurable pixel/metadata properties (color, light, texture, composition, EXIF, embedded text). No Haar cascades, no ML classifiers of any kind.

---

## 1. Dependencies

```txt
Pillow>=10.0
opencv-python>=4.9
numpy>=1.26
colorthief>=0.2.1
webcolors>=1.13
pytesseract>=0.3.10   # requires Tesseract OCR binary installed on the OS separately
Jinja2>=3.1
nltk>=3.8              # optional, for synonym variation
```
System dependency: `tesseract-ocr` binary must be installed at OS level (apt/brew/choco) — `pytesseract` is just a wrapper.

---

## 2. Project structure

```
image_to_blog/
├── __init__.py
├── config.py              # thresholds, bucket ranges, template lists
├── ingestion.py           # load/validate/normalize image
├── features/
│   ├── __init__.py
│   ├── color.py           # dominant palette + color naming
│   ├── light.py           # brightness, contrast, warmth
│   ├── texture.py         # sharpness, edge density
│   ├── composition.py     # focal point, orientation, busyness
│   ├── metadata.py        # EXIF extraction
│   └── text_ocr.py        # pytesseract text extraction
├── phrasing.py             # numeric feature -> descriptive word/phrase
├── templates/
│   ├── title.j2
│   ├── short_description.j2
│   └── long_description.j2
├── generator.py            # orchestrates: ingestion -> features -> phrasing -> templates -> output
└── api.py                  # single public function: generate_blog_text(image_path) -> dict
```

---

## 3. Module-by-module spec

### 3.1 `ingestion.py`
```python
def load_image(path_or_file) -> tuple[PIL.Image.Image, np.ndarray]:
    """
    - Open with Pillow, verify() for corruption, convert to RGB
    - Return both the PIL Image (for EXIF/OCR) and an OpenCV BGR numpy array (for CV features)
    - Raise a clear ValueError on unsupported/corrupt files
    """
```

### 3.2 `features/color.py`
```python
def dominant_colors(cv_image, k=5) -> list[tuple[int,int,int]]:
    """K-means (cv2.kmeans or ColorThief) on downsampled pixels -> top-k RGB colors, sorted by cluster size."""

def name_colors(rgb_list) -> list[str]:
    """Nearest-neighbor lookup against a webcolors/custom name table -> ['amber', 'charcoal', ...]"""
```

### 3.3 `features/light.py`
```python
def brightness_contrast(cv_image) -> dict:
    """Convert to grayscale; return {mean_brightness, std_contrast} via numpy histogram stats."""

def warmth_score(rgb_list) -> float:
    """Simple ratio of warm (R) vs cool (B) channel dominance across dominant colors -> -1 (cool) to +1 (warm)."""
```

### 3.4 `features/texture.py`
```python
def sharpness_score(cv_image) -> float:
    """Variance of Laplacian (cv2.Laplacian) -> higher = crisper/more detailed."""

def edge_density(cv_image) -> float:
    """Canny edge pixel count / total pixels -> proxy for visual complexity."""
```

### 3.5 `features/composition.py`
```python
def orientation(pil_image) -> str:
    """'landscape' | 'portrait' | 'square' from width/height."""

def focal_region(cv_image) -> str:
    """Divide image into 3x3 grid, find grid cell with highest edge density -> 'center','upper-left', etc. (rule-of-thirds proxy)."""

def busyness_label(edge_density_value) -> str:
    """Bucket edge_density into 'minimal' / 'balanced' / 'busy' via config thresholds."""
```

### 3.6 `features/metadata.py`
```python
def extract_exif(pil_image) -> dict:
    """Pull camera make/model, focal length, exposure, capture date, GPS (if present) via Pillow ExifTags."""
```

### 3.7 `features/text_ocr.py`
```python
def extract_text(pil_image) -> str:
    """pytesseract.image_to_string, cleaned/stripped. Return '' if nothing detected or low confidence."""
```

### 3.8 `phrasing.py`
```python
def brightness_phrase(mean_brightness: float) -> str: ...
def warmth_phrase(warmth: float) -> str: ...
def sharpness_phrase(score: float) -> str: ...
def busyness_phrase(label: str) -> str: ...
def mood_phrase(brightness, warmth, contrast) -> str:
    """Combine 2-3 signals into one mood word: 'moody', 'airy', 'vibrant', 'serene', 'dramatic'..."""
```
Each bucket should map to a **list** of 3-5 synonymous phrasings; pick via `random.choice` (seeded per-image hash for reproducibility if needed) so repeated generations don't feel identical.

### 3.9 `templates/*.j2` (Jinja2)
- `title.j2`: 2-3 short variants, e.g. `"{{ mood|capitalize }} Tones in {{ color1 }} & {{ color2 }}"`
- `short_description.j2`: 1-2 sentences combining mood + dominant colors + orientation
- `long_description.j2`: 3-5 sentences — mood, palette, composition/focal point, texture, EXIF detail (if present), OCR text (if present, phrased as *"The image includes the text '{{ ocr_text }}'"*)

### 3.10 `generator.py`
```python
def build_feature_dict(image_path) -> dict:
    """Call ingestion + all feature extractors, return one flat dict of raw feature values."""

def build_phrase_dict(feature_dict) -> dict:
    """Run phrasing.py functions over feature_dict -> dict of descriptive strings ready for templates."""

def render(phrase_dict) -> dict:
    """Render the three Jinja2 templates with phrase_dict -> {title, short_description, long_description}."""
```

### 3.11 `api.py` (single entrypoint)
```python
def generate_blog_text(image_path: str) -> dict:
    """
    features = build_feature_dict(image_path)
    phrases  = build_phrase_dict(features)
    return render(phrases)
    """
```
This is the only function the blog backend needs to import/call.

---

## 4. Build order (recommended sequence for Antigravity)

1. `ingestion.py` + a manual test script that loads a sample image and prints shape/mode
2. `features/color.py` — verify dominant colors visually (print swatches or save a palette strip image)
3. `features/light.py` + `features/texture.py` — print raw numeric values across 5-10 varied test images to sanity-check ranges before setting thresholds in `config.py`
4. `features/composition.py`
5. `features/metadata.py` and `features/text_ocr.py` (independent, can be built in parallel)
6. `config.py` — lock in bucket thresholds based on the numeric ranges observed in step 3
7. `phrasing.py` — write phrase banks per bucket
8. `templates/*.j2` — draft and iterate on wording
9. `generator.py` + `api.py` — wire everything together
10. Integration test: run `generate_blog_text()` against 10-15 diverse sample images (bright/dark, busy/minimal, portrait/landscape, with/without text) and manually review output quality; tune thresholds/phrase banks

---

## 5. Testing checklist
- [ ] Corrupt/unsupported file → clean error, not a crash
- [ ] Very small image (<100px) → features still compute without divide-by-zero
- [ ] Grayscale/CMYK source image → correctly converted to RGB before processing
- [ ] Image with no EXIF data → `extract_exif` returns empty dict gracefully, templates skip that sentence
- [ ] Image with no visible text → OCR returns '', templates skip that sentence
- [ ] Same image run twice → title/description vary slightly (randomized phrasing) but stay coherent

---

## 6. Known limitation to document in your repo README
This module describes an image's **visual properties**, not its subject matter (it cannot identify objects, people, or scenes). Flag this clearly wherever the feature is surfaced so it sets the right expectation for blog authors using it.
