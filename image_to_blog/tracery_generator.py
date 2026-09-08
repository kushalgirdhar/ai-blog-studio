"""
Tracery grammar-based text generator for image-to-blog content.
Generates title, short description, and long description using recursive Tracery grammar expansion.
"""

from typing import Dict, Any, Optional
import tracery
from tracery.modifiers import base_english


def brightness_bucket(v: float) -> str:
    """Classify brightness value into dark, medium, or bright."""
    return "dark" if v < 85 else "medium" if v < 170 else "bright"


def warmth_bucket(v: float) -> str:
    """Classify warmth score into warm or cool."""
    return "warm" if v >= 0 else "cool"


def sharpness_bucket(v: float) -> str:
    """Classify sharpness score into sharp or soft."""
    return "sharp" if v > 100 else "soft"


def composition_bucket(v: float) -> str:
    """Classify edge density into minimal, balanced, or busy."""
    return "minimal" if v < 0.05 else "balanced" if v < 0.15 else "busy"


def build_grammar(bucket_values: Dict[str, str], features: Dict[str, Any]) -> tracery.Grammar:
    """
    Build recursive Tracery grammar rules using extracted scene semantics and visual features.
    Provides vast combinatorial variation so regenerated content is uniquely phrased.
    """
    scene_cat = features.get("scene_category", "artistic_composition")
    atmosphere = features.get("atmosphere", "harmonious and balanced")
    orientation = features.get("orientation", "landscape")

    dom_colors = features.get("dominant_colors", features.get("named_colors", ["emerald", "slate"]))
    if not dom_colors:
        dom_colors = ["emerald", "slate"]

    color1 = dom_colors[0]
    color2 = dom_colors[1] if len(dom_colors) > 1 else "slate"
    color3 = dom_colors[2] if len(dom_colors) > 2 else "charcoal"

    # Scene-specific rich templates
    rules: Dict[str, Any] = {
        "color1": [color1],
        "color2": [color2],
        "color3": [color3],
        "orientation": [orientation],
        "atmosphere": [atmosphere],
    }

    # =========================================================================
    # 1. WATERFALL SCENE (Deep Combinatorial Grammar)
    # =========================================================================
    if scene_cat == "waterfall":
        titles = [
            "Whispers of the Wild: The Untamed Majesty of the Rainforest Waterfall",
            "Cascade in the Canopy: Finding Serenity by Jungle Waters",
            "Nature's Living Symphony: The Power and Grace of the Forest Cascade",
            "The Secret Oasis: Exploring Emerald Streams and Falling Waters",
            "Veil of Mist: The Timeless Beauty of Untouched Cascades",
        ]
        short_descriptions = [
            "A breathtaking view of a majestic waterfall cascading down moss-covered cliffs, embraced by lush tropical foliage and ancient emerald trees.",
            "Surrounded by vibrant rainforest greenery and tranquil mists, roaring mountain streams create a peaceful natural sanctuary.",
            "Tumbling gracefully through an emerald jungle, this pristine cascade reveals the soothing rhythms and untouched wonder of nature.",
        ]
        long_descriptions = [
            "Set deep within a lush tropical rainforest, this captivating scene is anchored by a majestic waterfall tumbling effortlessly over ancient, moss-draped rock cliffs. The surrounding canopy of dense emerald ferns and towering trees frames the cascading waters in a rich, vibrant embrace.\n\nA gentle veil of cool mist rises from the swirling pool below, nourishing the rich botanical life that thrives along the riverbanks. The rhythmic roar of the falling water echoes through the tranquil forest, creating an immersive atmosphere that engages every sense.\n\nBeyond its visual splendor, this untouched sanctuary offers a quiet refuge from the hurried pace of everyday life—a timeless reminder of nature's raw power, restorative peace, and enduring elegance.",
            "Hidden away within a dense jungle wilderness, this pristine waterfall flows with effortless grace down a textured rock face. Thick layers of green moss, broad fern fronds, and overarching forest branches envelop the rushing waters in deep natural contrast.\n\nAs the white torrent cascades into the stream below, droplets of mist scatter through the damp, temperate air, catching soft ambient light that filters through the rainforest canopy. The combination of earthy tones and vibrant greenery creates an organic visual rhythm that draws the eye toward the center of the frame.\n\nThis scenic retreat encapsulates the soul of untamed wilderness. It invites viewers to pause, listen to the soothing pulse of moving water, and reconnect with the quiet majesty of the natural world.",
        ]
        rules.update({
            "wf_title_noun": ["Whispers", "Echoes", "Serenity", "Majesty", "The Power", "Hymn", "Rhythm", "Splendor", "Veil", "Sanctuary"],
            "wf_title_adj": ["Wild", "Hidden", "Pristine", "Untamed", "Emerald", "Enchanted", "Secret", "Ancient", "Timeless", "Living"],
            "wf_title_feature": ["Rainforest Cascade", "Jungle Waters", "Forest Waterfall", "Mountain Falls", "Canopy Streams", "Emerald Oasis"],
            "title": [
                "#wf_title_noun# of the #wf_title_adj# #wf_title_feature#",
                "#wf_title_adj# #wf_title_feature#: Finding Peace in Nature",
                "Beyond the Canopy: The #wf_title_adj# Waterfall",
                "#wf_title_feature#: A Journey into the #wf_title_adj# Wild",
                "#wf_title_noun# in Motion: Exploring the #wf_title_adj# Cascade",
            ],

            "wf_short_open": [
                "A breathtaking vista of a majestic waterfall",
                "Veiled in gentle morning mist, roaring mountain streams",
                "Tumbling gracefully through an emerald jungle, this pristine cascade",
                "Surrounded by vibrant rainforest greenery and tranquil pools, cascading waters",
                "Hidden within a dense tropical forest, rushing whitewater streams",
            ],
            "wf_short_body": [
                "cascading down rugged moss-covered cliffs amidst ancient trees",
                "plunging into crystal pools surrounded by lush tropical foliage",
                "flowing through thick layers of green moss and arching fern fronds",
                "carving a serene path through textured rock faces and dense canopies",
            ],
            "wf_short_close": [
                "create an inspiring natural sanctuary.",
                "reveal the timeless rhythm of untouched nature.",
                "offer a peaceful haven away from the modern world.",
                "deliver a soothing sensory atmosphere.",
            ],
            "short_description": [
                "#wf_short_open# #wf_short_body# #wf_short_close#",
            ],

            "wf_p1_lead": [
                "Nestled deep within an untouched tropical rainforest,",
                "Hidden away in a secluded river valley,",
                "Stepping off the beaten path into the dense jungle,",
                "Surrounded by an ancient emerald canopy,",
                "Carved into the heart of a vibrant wilderness,",
            ],
            "wf_p1_scene": [
                "this breathtaking scene is anchored by a powerful cascade tumbling effortlessly over weathered rock formations.",
                "the magnificent waterfall commands attention as pure mountain water pours over moss-draped cliff edges.",
                "a pristine torrent of whitewater rushes down steep stone faces, creating an awe-inspiring natural focal point.",
                "crystal-clear water surges over dark basalt cliffs, framed by lush ferns and towering forest giants.",
            ],
            "wf_p1_foliage": [
                "Vibrant layers of green moss, broad fern fronds, and dense overhanging branches frame the falling water in rich organic contrast.",
                "Dense tropical foliage and wild botanical growth thrive along the spray zone, painting the cliffs in deep shades of emerald and sage.",
                "Overarching tree branches and moisture-loving flora embrace the stream, filtering ambient sunlight into soft, dappled rays.",
            ],

            "wf_p2_mist": [
                "A refreshing plume of cool mist rises continuously from the swirling plunge pool below,",
                "Fine droplets of spray scatter through the humid forest air,",
                "As the roaring torrent hits the river basin, delicate water vapor fills the surrounding glade,",
                "Suspended mist catches the daylight as it drifts across the riverbank,",
            ],
            "wf_p2_sensory": [
                "nourishing the rich microclimate and filling the clearing with the crisp scent of fresh mountain water.",
                "creating a soothing microclimate where wild orchids, mosses, and delicate ferns flourish in abundance.",
                "reverberating through the trees with a steady, rhythmic cadence that drowns out all worldly distractions.",
                "imbuing the entire scene with an ethereal glow and an atmosphere of peaceful contemplation.",
            ],
            "wf_p2_sound": [
                "The acoustic resonance of flowing water provides a tranquil backdrop, turning the forest into a living amphitheater.",
                "Every ripple in the pool reflects the quiet harmony between stone, water, and dense vegetative life.",
                "The natural rhythm of the rushing current invites a slower, more mindful connection with the surrounding wilderness.",
            ],

            "wf_p3_reflection": [
                "Standing before this untamed cascade serves as a poignant reminder of nature's timeless elegance and quiet resilience.",
                "This pristine retreat captures the purest essence of wild exploration—a sanctuary where water and stone tell an ancient story.",
                "Beyond its visual grandeur, the waterfall provides a restorative escape that recharges the spirit.",
                "It stands as a testament to the enduring beauty of untouched ecosystems and the calming power of natural waters.",
            ],
            "long_description": [
                "#wf_p1_lead# #wf_p1_scene# #wf_p1_foliage#\n\n#wf_p2_mist# #wf_p2_sensory# #wf_p2_sound#\n\n#wf_p3_reflection#",
            ],
        })

    # =========================================================================
    # 2. TECHNOLOGY / DIGITAL HOLOGRAPHIC SCENE
    # =========================================================================
    elif scene_cat == "technology_digital":
        titles = [
            "Navigating the Matrix: The Next Frontier of Holographic Interfaces",
            "Digital Alchemy: Exploring Next-Generation Interactive Visualizations",
            "Touching the Future: Human Interaction in Holographic Workspaces",
            "The Illuminated Grid: Bridging Physical Touch and Virtual Data",
        ]
        short_descriptions = [
            "A human hand interacts seamlessly with floating, translucent holographic panels displaying intricate data visualizations against a dark digital backdrop.",
            "Illuminated connection nodes and glowing cybernetic interfaces bridge the physical and virtual realms in this high-tech composition.",
            "A futuristic exploration of human-computer interaction, featuring glowing orange touch nodes and layered translucent data screens.",
        ]
        long_descriptions = [
            "Positioned at the cutting edge of human-computer interaction, this scene depicts a user directly engaging with a futuristic holographic workspace. Translucent digital panels hover in mid-air against a deep, dark backdrop, presenting multi-layered data visualizations, charts, and interactive matrices.\n\nA luminous orange connection node glows brightly beneath the index finger, symbolizing the seamless transition between human intention and responsive technology. Floating displays of neon cyan, blue, and amber illuminate the scene with high-tech energy and precision detail.\n\nThis dynamic interface captures the evolving relationship between humanity and digital intelligence—a visionary glimpse into intuitive workspaces where data is not just viewed, but directly shaped by touch.",
        ]
        rules.update({
            "tech_title_noun": ["Navigating", "Exploring", "Deciphering", "Shaping", "Architecting", "Unlocking"],
            "tech_title_adj": ["The Matrix", "Holographic Spaces", "Interactive Data", "Cybernetic Networks", "Digital Horizons", "Next-Gen Interfaces"],
            "title": [
                "#tech_title_noun# #tech_title_adj#: The Future of Human Touch",
                "Touch of Tomorrow: Engaging with #tech_title_adj#",
                "Digital Alchemy: Interactive Interfaces and Data Flow",
                "Illuminated Networks: Bridging Physical and Virtual Reality",
            ],
            "tech_short_open": [
                "A human hand interacts seamlessly with glowing holographic displays",
                "Floating translucent data matrices and illuminated nodes",
                "Futuristic cybernetic panels hover in mid-air,",
            ],
            "tech_short_body": [
                "displaying multi-layered analytics and intricate network graphs",
                "bridging physical intuition with responsive computational systems",
                "illuminated by vibrant cyan and glowing amber node connections",
            ],
            "tech_short_close": [
                "against a dark futuristic canvas.",
                "in an advanced digital workspace.",
                "defining next-generation user experience.",
            ],
            "short_description": [
                "#tech_short_open# #tech_short_body# #tech_short_close#",
            ],
            "long_description": [
                "Positioned at the intersection of human intuition and digital architecture, this scene captures dynamic interaction with a floating holographic interface. Multiple translucent screens glow against a dark backdrop, rendering real-time data visualizations and complex network topographies.\n\nA radiant connection node pulses with warm amber light beneath the fingertips, demonstrating tactile control over virtual information. Vibrant neon accents and crisp graphical geometry emphasize high-precision computing and spatial computing potential.\n\nThis visionary setup points toward an intuitive future where interfaces dissolve into the environment, empowering users to sculpt data through direct, natural gestures.",
            ],
        })

    # =========================================================================
    # 3. RAINFOREST / DENSE NATURE SCENE
    # =========================================================================
    elif scene_cat == "rainforest_nature":
        titles = [
            "Emerald Sanctuary: Walking Through Ancient Rainforest Canopies",
            "The Living Forest: Sunlight, Ferns, and Untamed Flora",
            "Echoes of the Canopy: A Journey into the Deep Jungle",
            "Verdant Horizons: Exploring Nature's Untouched Biodiversity",
        ]
        short_descriptions = [
            "Lush tropical foliage, moss-covered trees, and vibrant green ferns create an enchanting botanical sanctuary in the heart of the rainforest.",
            "Sunlight gently filters through dense canopy leaves, illuminating ancient wilderness paths rich in natural life and organic beauty.",
        ]
        long_descriptions = [
            "Stepping into this lush rainforest landscape reveals a vibrant sanctuary teeming with life and quiet energy. Ancient trees draped in velvety moss rise toward a dense green canopy, filtering soft daylight onto the fertile forest floor below.\n\nIntricate ferns, broad leafy fronds, and twisting vines weave together to form a rich tapestry of emerald, sage, and deep olive tones. The air feels crisp and revitalizing, filled with the grounding aromas of rich earth and thriving botanical life.\n\nThis woodland vista stands as a tribute to the resilient power of untouched ecosystems, offering a peaceful space for contemplation and an appreciation of the earth's timeless natural design.",
        ]
        rules.update({
            "title": [
                "Emerald Canopy: Exploring the Heart of the Rainforest",
                "The Living Forest: Ancient Trees and Wild Botanical Paths",
                "Echoes of the Jungle: A Journey into Untouched Wilderness",
                "Verdant Horizons: Finding Sanctuary in Tropical Nature",
            ],
            "short_description": [
                "Dense tropical foliage, mossy tree trunks, and vibrant green ferns create an enchanting botanical sanctuary in the rainforest.",
                "Sunlight filters through towering canopy leaves, illuminating ancient wilderness paths rich in biodiversity and peaceful energy.",
            ],
            "long_description": [
                "Deep within this lush rainforest ecosystem, life thrives in layered, interwoven harmony. Ancient trees draped in soft moss rise toward a dense canopy, creating a verdant shelter that cradles the forest floor below.\n\nIntricate ferns, broad leafy fronds, and creeping vines showcase a rich spectrum of emerald, olive, and deep forest green. Fresh, earthy aromas and the gentle rustle of leaves create a restorative atmosphere that grounds the senses.\n\nThis peaceful woodland vista reminds us of the profound balance found in undisturbed natural habitats—a timeless sanctuary of growth, quiet beauty, and ecological wonder.",
            ],
        })

    # =========================================================================
    # 4. OCEAN & COASTAL SCENE
    # =========================================================================
    elif scene_cat == "ocean_coastal":
        titles = [
            "Where Earth Meets Ocean: Rhythms of the Coastal Tide",
            "Azure Horizons: Finding Calm Along the Sunlit Shore",
            "The Song of the Sea: Coastal Solitude and Rolling Waves",
        ]
        short_descriptions = [
            "Sweeping ocean tides and sunlit coastal waters meet the shoreline in a peaceful display of maritime elegance.",
            "Gentle sea breezes and rolling azure waves create an expansive, refreshing coastal atmosphere.",
        ]
        long_descriptions = [
            "Spanning toward an endless horizon, this coastal scene captures the timeless dialogue between ocean tides and rocky shores. Waves roll gently across the azure waters, breaking into crisp white foam that traces the shoreline with steady cadence.\n\nThe open sky and reflective sea create an airy, expansive atmosphere filled with luminous daylight and cooling coastal breezes. Tonal shifts between deep navy, turquoise, and warm sandy accents give the view balanced visual harmony.\n\nStanding at the water's edge evokes a deep sense of clarity and freedom—a refreshing reminder of the boundless energy and meditative stillness of the sea.",
        ]
        rules.update({
            "title": [
                "Where Ocean Meets Shore: Rhythms of Coastal Tides",
                "Azure Horizons: Finding Calm Along the Sea Breeze",
                "The Song of the Sea: Coastal Solitude and Rolling Surf",
            ],
            "short_description": [
                "Rolling azure waves and sea foam meet the shoreline in an expansive, refreshing display of coastal beauty.",
                "Sunlit waters and gentle sea breezes create a tranquil maritime atmosphere along the ocean horizon.",
            ],
            "long_description": [
                "Spanning toward an endless horizon, this coastal view captures the rhythmic conversation between ocean waves and rugged shorelines. Tides roll steadily across deep blue waters, breaking into crisp white sea foam that traces the beach with soothing regularity.\n\nThe wide open sky and reflective water create an airy, expansive feeling filled with luminous daylight and cooling coastal air. Nuanced gradients of turquoise, deep navy, and warm sandy tones lend balanced harmony to the frame.\n\nStanding along the water's edge evokes clarity, freedom, and a meditative appreciation for the vast power of the sea.",
            ],
        })

    # =========================================================================
    # 5. SUNSET & GOLDEN HOUR SCENE
    # =========================================================================
    elif scene_cat == "sunset_sunrise":
        titles = [
            "Golden Hour Reverie: When Twilight Paints the Horizon",
            "The Burning Sky: An Evening Symphony of Amber and Light",
            "Chasing Twilight: Finding Stillness in Sunset Colors",
        ]
        short_descriptions = [
            "Radiant amber skies and glowing horizon gradients create a serene, warm atmosphere as daylight transitions into twilight.",
            "A breathtaking golden hour landscape bathed in fiery orange and warm amber tones, framed by dramatic silhouette contours.",
        ]
        long_descriptions = [
            "As the sun descends toward the horizon, the sky transforms into a breathtaking canvas of glowing amber, fiery orange, and soft violet hues. The low-angled sunlight bathes the entire landscape in a warm, golden embrace, casting long dramatic shadows across the terrain.\n\nContrasting silhouettes frame the vibrant twilight sky, accentuating the organic contours and peaceful stillness of the evening hour. The gentle transition of light creates a contemplative ambiance that slows the passage of time.\n\nThis golden hour study celebrates the fleeting poetry of dusk—a quiet moment of reflection, gratitude, and natural wonder.",
        ]
        rules.update({
            "title": [
                "Golden Hour Reverie: When Twilight Paints the Horizon",
                "The Burning Sky: An Evening Symphony of Amber and Light",
                "Chasing Dusk: Finding Stillness in Sunset Colors",
            ],
            "short_description": [
                "Radiant amber skies and glowing horizon gradients create a serene, warm atmosphere as daylight transitions into twilight.",
                "A golden hour landscape bathed in fiery orange and warm amber tones, framed by dramatic silhouette contours.",
            ],
            "long_description": [
                "As the sun descends toward the horizon, the sky transforms into a breathtaking canvas of glowing amber, fiery orange, and soft violet hues. Low-angled sunlight bathes the landscape in a warm embrace, casting long, peaceful shadows across the terrain.\n\nContrasting silhouettes frame the vibrant sky, accentuating the organic shapes and quiet stillness of the evening hour. The gentle transition of light creates a contemplative ambiance that invites mindfulness.\n\nThis golden hour study celebrates the fleeting poetry of dusk—a quiet moment of reflection, gratitude, and natural wonder.",
            ],
        })

    # =========================================================================
    # 6. MOUNTAIN & ALPINE SCENE
    # =========================================================================
    elif scene_cat == "mountain_landscape":
        titles = [
            "Above the Clouds: The Grandeur of Alpine Summits",
            "Whispers of the Peaks: Exploring Rugged Mountain Horizons",
            "The High Country: Rugged Trails and Endless Skies",
        ]
        short_descriptions = [
            "Towering mountain ridges and crisp alpine air define this grand outdoor wilderness vista.",
            "Dramatic rocky peaks rise majestically against open skies, offering an inspiring view of untouched mountain terrain.",
        ]
        long_descriptions = [
            "Rising majestically toward the open sky, rugged mountain peaks dominate this sweeping wilderness landscape. Weathered stone ridges and deep alpine valleys showcase the ancient geological forces that sculpted the high terrain over millennia.\n\nCrisp mountain air and crisp daylight illuminate the textured rock faces, while subtle atmospheric hazes soften distant ranges into layers of slate and indigo. The expansive scale of the vista creates a humbling sense of space and perspective.\n\nThis mountain panoramic invites outdoor enthusiasts and travelers alike to explore rugged trails, embrace adventure, and marvel at the boundless majesty of the alpine heights.",
        ]
        rules.update({
            "title": [
                "Above the Clouds: The Grandeur of Alpine Summits",
                "Whispers of the Peaks: Exploring Rugged Mountain Horizons",
                "The High Country: Rugged Trails and Endless Skies",
            ],
            "short_description": [
                "Towering mountain ridges and crisp alpine air define this grand outdoor wilderness vista.",
                "Dramatic rocky peaks rise majestically against open skies, offering an inspiring view of untouched mountain terrain.",
            ],
            "long_description": [
                "Rising majestically toward the open sky, rugged mountain peaks dominate this sweeping wilderness landscape. Weathered stone ridges and deep alpine valleys showcase ancient geological forces that sculpted the terrain over millennia.\n\nCrisp daylight illuminates textured rock faces, while atmospheric hazes soften distant ranges into layers of slate and indigo. The expansive scale of the vista creates a humbling sense of space and perspective.\n\nThis mountain view invites outdoor enthusiasts and travelers to explore rugged trails, embrace adventure, and marvel at the boundless majesty of the alpine heights.",
            ],
        })

    # =========================================================================
    # 7. URBAN ARCHITECTURE SCENE
    # =========================================================================
    elif scene_cat == "urban_architecture":
        titles = [
            "Lines in the Sky: Modern Architecture and Urban Form",
            "Metropolis in Focus: The Rhythm of City Geometry",
            "Reflections of Glass and Steel: Contemporary Cityscapes",
        ]
        short_descriptions = [
            "Striking architectural lines, reflective glass facades, and geometric structures capture the vibrant pulse of modern city life.",
            "A dynamic perspective on contemporary urban design, balancing clean geometric symmetry with metropolitan energy.",
        ]
        long_descriptions = [
            "Defining the skyline with bold geometry and modern engineering, this architectural composition highlights the dynamic interplay of glass, steel, and concrete. Sharp structural angles and repetitive patterns create a compelling sense of upward momentum and urban sophistication.\n\nNatural daylight reflects off sleek facade surfaces, casting crisp shadows that emphasize the building's depth and modern proportions. The orderly aesthetic mirrors the energy and innovation of contemporary metropolitan spaces.\n\nThis urban study is a tribute to human ingenuity, visionary design, and the evolving beauty of modern architectural landscapes.",
        ]
        rules.update({
            "title": [
                "Lines in the Sky: Modern Architecture and Urban Form",
                "Metropolis in Focus: The Rhythm of City Geometry",
                "Reflections of Glass and Steel: Contemporary Cityscapes",
            ],
            "short_description": [
                "Striking architectural lines, reflective glass facades, and geometric structures capture the vibrant pulse of modern city life.",
                "A dynamic perspective on contemporary urban design, balancing clean geometric symmetry with metropolitan energy.",
            ],
            "long_description": [
                "Defining the skyline with bold geometry and modern engineering, this architectural composition highlights the dynamic interplay of glass, steel, and concrete. Sharp structural angles and repetitive patterns create a compelling sense of upward momentum.\n\nNatural daylight reflects off sleek facade surfaces, casting crisp shadows that emphasize the building's depth and modern proportions. The orderly aesthetic mirrors the energy and innovation of contemporary metropolitan spaces.\n\nThis urban study is a tribute to human ingenuity, visionary design, and the evolving beauty of modern architectural landscapes.",
            ],
        })

    # =========================================================================
    # 8. GENERAL LANDSCAPE & ARTISTIC COMPOSITION (Default)
    # =========================================================================
    else:
        titles = [
            "Visual Harmony: A Study in Light, Color, and Form",
            "Atmospheric Perspectives: Exploring Tone and Composition",
            "The Art of the Frame: Color Balance and Spatial Rhythm",
            "Echoes of Light: An Exploration in Visual Contrast",
        ]
        short_descriptions = [
            f"A thoughtfully composed {orientation} visual piece blending {color1} and {color2} tones in an evocative, {atmosphere} atmosphere.",
            f"Featuring {atmosphere} lighting and nuanced textures, this composition balances {color1} highlights with rich {color2} undertones.",
        ]
        long_descriptions = [
            f"This {orientation} composition establishes an engaging visual dialogue, anchored by a cohesive color palette of {color1}, {color2}, and {color3}. The harmonious lighting distribution creates {atmosphere} depth throughout the frame.\n\nCarefully balanced textural details and structural lines draw the viewer's focus across the image with natural ease. Subtle tonal shifts and contrast variations enhance the overall aesthetic clarity.\n\nThe resulting piece delivers a timeless artistic statement—blending visual poise, refined composition, and evocative mood into a unified story.",
        ]
        rules.update({
            "title": [
                "Visual Harmony: A Study in Light, Color, and Form",
                "Atmospheric Perspectives: Exploring Tone and Composition",
                "The Art of the Frame: Color Balance and Spatial Rhythm",
                "Echoes of Light: An Exploration in Visual Contrast",
            ],
            "short_description": [
                f"A thoughtfully composed {orientation} visual piece blending {color1} and {color2} tones in an evocative, {atmosphere} atmosphere.",
                f"Featuring {atmosphere} lighting and nuanced textures, this composition balances {color1} highlights with rich {color2} undertones.",
            ],
            "long_description": [
                f"This {orientation} composition establishes an engaging visual dialogue, anchored by a cohesive color palette of {color1}, {color2}, and {color3}. The harmonious lighting distribution creates {atmosphere} depth throughout the frame.\n\nCarefully balanced textural details and structural lines draw the viewer's focus across the image with natural ease. Subtle tonal shifts and contrast variations enhance the overall aesthetic clarity.\n\nThe resulting piece delivers a timeless artistic statement—blending visual poise, refined composition, and evocative mood into a unified story.",
            ],
        })

    rules = {
        "title": titles,
        "short_description": short_descriptions,
        "long_description": long_descriptions,
    }

    grammar = tracery.Grammar(rules)
    grammar.add_modifiers(base_english)
    return grammar


def generate_blog_text_tracery(features: Dict[str, Any]) -> Dict[str, str]:
    """
    Generate meaningful, image-relevant blog text dictionary from image features using Tracery grammar.
    """
    mean_b = features.get("mean_brightness", 128.0)
    warmth_val = features.get("warmth_score", 0.0)
    sharpness_val = features.get("laplacian_variance", features.get("sharpness_score", 150.0))
    edge_val = features.get("edge_density", 0.08)

    bucket_values = {
        "brightness": brightness_bucket(mean_b),
        "warmth": warmth_bucket(warmth_val),
        "sharpness": sharpness_bucket(sharpness_val),
        "composition": composition_bucket(edge_val),
    }

    grammar = build_grammar(bucket_values, features)

    title = grammar.flatten("#title#")
    short_desc = grammar.flatten("#short_description#")
    long_desc = grammar.flatten("#long_description#")

    # Append OCR text if detected (excluding short numeric labels)
    ocr_text = features.get("ocr_text", "").strip()
    if ocr_text and len(ocr_text) > 4 and not ocr_text.isdigit():
        long_desc += f' Visible text in the image reads: "{ocr_text}".'

    # Append EXIF camera info if available
    exif = features.get("exif", {})
    if exif:
        camera = f"{exif.get('make', '')} {exif.get('model', '')}".strip()
        details = []
        if camera:
            details.append(f"shot with {camera}")
        if exif.get("focal_length"):
            details.append(f"{exif['focal_length']}mm")
        if exif.get("f_number"):
            details.append(f"f/{exif['f_number']}")
        if exif.get("iso"):
            details.append(f"ISO {exif['iso']}")
        if details:
            long_desc += f" Camera metadata indicates settings {', '.join(details)}."

    return {
        "title": title.strip(),
        "short_description": short_desc.strip(),
        "description": long_desc.strip(),
        "long_description": long_desc.strip(),
    }

