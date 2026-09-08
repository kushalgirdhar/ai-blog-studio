"""
Same job as text_generation_demo.py, but the WRITING side now uses
Tracery instead of plain Python random.choice() + Jinja2.

Tracery is a grammar-based generative text library (not a trained AI
model — no weights, no training data, no API). You define a grammar:
a dict of symbol -> list of possible expansions, where expansions can
reference OTHER symbols with #symbol# syntax. Tracery recursively
expands the grammar, picking randomly at each branch, and can also
apply grammar modifiers (like fixing "a" vs "an").

pip install tracery
"""

import tracery
from tracery.modifiers import base_english


# ---------------------------------------------------------------------------
# 1. Bucket logic — STILL plain Python.
#    This step just classifies raw numbers from the image-processing stage
#    (brightness=195.0, etc.) into categories. This isn't "text generation",
#    it's numeric classification, so a text-generation library doesn't
#    apply here — Tracery takes over from this point onward.
# ---------------------------------------------------------------------------

def brightness_bucket(v: float) -> str:
    return "dark" if v < 85 else "medium" if v < 170 else "bright"

def warmth_bucket(v: float) -> str:
    return "warm" if v >= 0 else "cool"

def sharpness_bucket(v: float) -> str:
    return "sharp" if v > 100 else "soft"

def composition_bucket(v: float) -> str:
    return "minimal" if v < 0.05 else "balanced" if v < 0.15 else "busy"


# ---------------------------------------------------------------------------
# 2. TRACERY GRAMMAR — this is the text-generation part.
#    Each symbol has a LIST of options; Tracery picks one at random
#    whenever that symbol is expanded. Symbols can nest other symbols
#    with #symbol_name#. This replaces your phrase-bank dicts +
#    random.choice() + Jinja2 templates all at once.
# ---------------------------------------------------------------------------

def build_grammar(bucket_values: dict, features: dict) -> tracery.Grammar:
    b, w, s, c = bucket_values["brightness"], bucket_values["warmth"], \
                 bucket_values["sharpness"], bucket_values["composition"]

    mood_options = {
        "dark":   ["moody", "low-key", "shadow-rich"],
        "medium": ["balanced", "even-toned", "natural"],
        "bright": ["bright", "airy", "luminous"],
    }[b]

    warmth_options = {
        "cool": ["cool-toned", "crisp and cool"],
        "warm": ["warm-toned", "golden", "sun-warmed"],
    }[w]

    sharp_options = {
        "soft":  ["soft-focused", "dreamy"],
        "sharp": ["crisp", "sharply detailed"],
    }[s]

    comp_options = {
        "minimal":  ["a minimal composition", "an uncluttered frame"],
        "balanced": ["a balanced composition", "a well-composed frame"],
        "busy":     ["a busy, detail-rich composition", "a visually dense frame"],
    }[c]

    rules = {
        "mood": mood_options,
        "warmth": warmth_options,
        "sharpness": sharp_options,
        "composition": comp_options,
        "color1": [features["dominant_colors"][0]],
        "color2": [features["dominant_colors"][1]] if len(features["dominant_colors"]) > 1 else [""],
        "orientation": [features["orientation"]],

        # Tracery recursively expands #symbol# references below,
        # and .a applies correct "a"/"an" grammar automatically.
        "title": ["#mood.capitalize# #color1# & #color2# Moments"],
        "short_description": [
            "#mood.a# #color1# #orientation# scene, #warmth# with #sharpness# detail."
        ],
        "long_description": [
            "This #orientation# image gives off #mood.a# feel, "
            "built around #color1# and #color2# tones. "
            "The image is #sharpness#, set within #composition#."
        ],
    }

    grammar = tracery.Grammar(rules)
    grammar.add_modifiers(base_english)  # enables .capitalize, .a, .s, etc.
    return grammar


def generate_blog_text(features: dict) -> dict:
    bucket_values = {
        "brightness": brightness_bucket(features["mean_brightness"]),
        "warmth": warmth_bucket(features["warmth_score"]),
        "sharpness": sharpness_bucket(features["laplacian_variance"]),
        "composition": composition_bucket(features["edge_density"]),
    }

    grammar = build_grammar(bucket_values, features)

    result = {
        "title": grammar.flatten("#title#"),
        "short_description": grammar.flatten("#short_description#"),
        "long_description": grammar.flatten("#long_description#"),
    }

    if features.get("ocr_text"):
        result["long_description"] += f' Visible text in the image reads: "{features["ocr_text"]}".'

    return result


# ---------------------------------------------------------------------------
# DEMO
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    fake_features_from_image_processing_stage = {
        "mean_brightness": 195.0,
        "warmth_score": 0.6,
        "laplacian_variance": 140.0,
        "edge_density": 0.04,
        "dominant_colors": ["amber", "charcoal"],
        "orientation": "landscape",
        "ocr_text": "SALE 50% OFF",
    }

    for i in range(3):
        out = generate_blog_text(fake_features_from_image_processing_stage)
        print(f"--- run {i+1} ---")
        print("TITLE:", out["title"])
        print("SHORT:", out["short_description"])
        print("LONG: ", out["long_description"])
        print()
