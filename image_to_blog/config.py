"""Configuration constants, thresholds, color definitions, and phrase banks for image_to_blog."""

# Color mapping: name -> (R, G, B)
COLOR_PALETTE = {
    "black": (0, 0, 0),
    "charcoal": (40, 40, 40),
    "slate gray": (112, 128, 144),
    "silver": (192, 192, 192),
    "white": (255, 255, 255),
    "ivory": (255, 255, 240),
    "cream": (253, 245, 230),
    "crimson": (220, 20, 60),
    "scarlet": (255, 36, 0),
    "ruby red": (155, 17, 30),
    "burgundy": (128, 0, 32),
    "maroon": (128, 0, 0),
    "coral": (255, 127, 80),
    "salmon": (250, 128, 114),
    "rose pink": (255, 102, 204),
    "dusty rose": (214, 142, 156),
    "magenta": (255, 0, 255),
    "plum": (142, 69, 133),
    "deep purple": (75, 0, 130),
    "lavender": (230, 230, 250),
    "violet": (138, 43, 226),
    "navy blue": (0, 0, 128),
    "midnight blue": (25, 25, 112),
    "royal blue": (65, 105, 225),
    "cobalt blue": (0, 71, 171),
    "sky blue": (135, 206, 235),
    "cyan": (0, 255, 255),
    "teal": (0, 128, 128),
    "turquoise": (64, 224, 208),
    "aquamarine": (127, 255, 212),
    "emerald green": (80, 200, 120),
    "forest green": (34, 139, 34),
    "sage green": (158, 169, 142),
    "olive green": (107, 142, 35),
    "moss green": (138, 154, 91),
    "lime green": (50, 205, 50),
    "mint green": (152, 251, 152),
    "golden yellow": (255, 215, 0),
    "amber": (255, 191, 0),
    "warm ochre": (204, 119, 34),
    "mustard": (227, 180, 72),
    "apricot": (251, 206, 177),
    "tangerine": (242, 133, 0),
    "terracotta": (226, 114, 91),
    "rust orange": (183, 65, 14),
    "copper": (184, 115, 51),
    "bronze": (205, 127, 50),
    "chocolate brown": (92, 64, 51),
    "espresso": (54, 43, 40),
    "coffee brown": (111, 78, 55),
    "caramel": (198, 142, 85),
    "warm beige": (245, 245, 220),
    "taupe": (179, 139, 109),
    "khaki": (240, 230, 140),
}

# Numeric thresholds
THRESHOLDS = {
    "brightness": {
        "dark": 60,
        "medium_dark": 100,
        "balanced": 160,
        "bright": 210,
    },
    "contrast": {
        "low": 35.0,
        "moderate": 65.0,
    },
    "warmth": {
        "cool": -0.15,
        "warm": 0.15,
    },
    "sharpness": {
        "soft": 100.0,
        "moderate": 400.0,
    },
    "edge_density": {
        "minimal": 0.04,
        "balanced": 0.12,
    },
}

# Phrase collections for dynamic phrasing
PHRASE_BANKS = {
    "brightness": {
        "dark": [
            "deeply shadowed lighting",
            "low-key ambiance with deep shadows",
            "moody, understated lighting",
            "rich, dark atmosphere",
        ],
        "medium_dark": [
            "gentle, subdued illumination",
            "soft ambient lighting with balanced shadow",
            "dim, introspective lighting",
            "moderate low-light exposure",
        ],
        "balanced": [
            "evenly balanced exposure",
            "natural, harmonious lighting",
            "well-diffused daylight conditions",
            "balanced illumination across the frame",
        ],
        "bright": [
            "bright, luminous illumination",
            "vibrant and well-lit scene",
            "clear, radiant daylight",
            "high clarity with abundant light",
        ],
        "high_key": [
            "brilliant, high-key lighting",
            "dazzling and radiant exposure",
            "bright, airy highlights",
            "intensely lit visual presentation",
        ],
    },
    "contrast": {
        "low": [
            "soft gradations and subtle tonal transitions",
            "gentle, low-contrast tonality",
            "dreamy, muted contrast",
        ],
        "moderate": [
            "natural tonal contrast and distinct separation",
            "balanced depth between light and shadow",
            "pleasing dynamic range",
        ],
        "high": [
            "dramatic contrast between highlights and deep shadows",
            "bold dynamic punch and defined shapes",
            "striking contrast with strong visual separation",
        ],
    },
    "warmth": {
        "cool": [
            "crisp, cool undertones",
            "refreshing cool-toned spectrum",
            "tranquil, bluish atmosphere",
            "calm, cool aesthetic",
        ],
        "neutral": [
            "natural, neutral color temperature",
            "balanced and true-to-life color grading",
            "harmonious, neutral temperature balance",
        ],
        "warm": [
            "cozy, warm golden undertones",
            "inviting warm-hued radiance",
            "amber and earth-toned warmth",
            "sun-kissed warm temperature",
        ],
    },
    "sharpness": {
        "soft": [
            "softly rendered textures and gentle focus",
            "subtle, smooth transitions with dreamlike diffusion",
            "gentle textural gradients",
        ],
        "moderate": [
            "clean focus and well-defined contours",
            "crisp details across the subject",
            "neat textural fidelity",
        ],
        "sharp": [
            "razor-sharp micro-details and crisp edge definition",
            "high visual acuity and pristine structural clarity",
            "vividly articulated details and clear silhouettes",
        ],
    },
    "busyness": {
        "minimal": [
            "a minimalist aesthetic with expansive negative space",
            "clean, uncluttered visual breathing room",
            "a serene, focused presentation",
        ],
        "balanced": [
            "a well-proportioned visual balance",
            "harmoniously structured elements throughout the frame",
            "an orderly, engaging compositional rhythm",
        ],
        "busy": [
            "a visually intricate and detailed arrangement",
            "rich, layered visual complexity",
            "a dynamic, information-dense composition",
        ],
    },
    "mood": {
        "mysterious_dark": ["enigmatic", "moody", "contemplative", "dramatic"],
        "warm_inviting": ["cozy", "warm", "inviting", "golden"],
        "cool_serene": ["serene", "crisp", "tranquil", "peaceful"],
        "vibrant_energetic": ["vibrant", "dynamic", "spirited", "expressive"],
        "clean_minimal": ["refined", "minimalist", "sleek", "understated"],
        "balanced_classic": ["harmonious", "balanced", "timeless", "distinctive"],
    },
}

