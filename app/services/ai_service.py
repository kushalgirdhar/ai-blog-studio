import base64
import json
import mimetypes

from groq import Groq
from config import Config

client = Groq(api_key=Config.GROQ_API_KEY)


def generate_blog_from_image(image_path):
    # Read image
    with open(image_path, "rb") as image_file:
        image_data = base64.b64encode(image_file.read()).decode("utf-8")

    # Detect image MIME type
    mime_type, _ = mimetypes.guess_type(image_path)

    if not mime_type:
        mime_type = "image/jpeg"

    response = client.chat.completions.create(
        model="qwen/qwen3.8-27b",
        max_completion_tokens=700,
        reasoning_effort="none",
        temperature=0.3,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "image_blog_draft",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "short_description": {"type": "string"},
                        "description": {"type": "string"},
                    },
                    "required": ["title", "short_description", "description"],
                    "additionalProperties": False,
                },
            },
        },
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """
You are a highly accurate image-grounded content writer.

Your task is to create a blog draft based ONLY on what can be visually verified
from the uploaded image.

Before writing the final content, mentally perform these two stages.

STAGE 1 — VISUAL OBSERVATION

Carefully inspect the image and identify only observable details:

- Main subject
- Objects
- People, if clearly visible
- Animals, if clearly visible
- Environment
- Background
- Foreground
- Colors
- Shapes
- Textures
- Visible actions or movement
- Composition
- Any clearly readable text

Do NOT assume information that is not visually verifiable.

STAGE 2 — BLOG CREATION

Using ONLY the visual observations from Stage 1, create:

1. TITLE
2. SHORT DESCRIPTION
3. LONG DESCRIPTION

GROUNDING RULES:

- Every factual statement must be supported by something visible in the image.
- Do not invent a location.
- Do not guess a country, city, landmark, tourist destination, or region.
- Do not guess the season, weather, climate, temperature, or time of day.
- Do not identify plant, animal, or object species unless identification is visually obvious.
- Do not invent historical, cultural, geographical, or scientific information.
- Do not assume the image is famous, remote, untouched, ancient, hidden, or pristine.
- Do not create a fictional story.
- Do not add information about people that cannot be seen.
- Do not claim photographic techniques unless they are clearly evident and necessary.
- If you are uncertain about something, describe it generically.
- Prefer concrete visual observations over emotional storytelling.
- Avoid exaggerated words such as "breathtaking", "majestic",
  "extraordinary", "unforgettable", "magical", "untouched",
  or "paradise" unless the image genuinely supports the description.
- Do not mention that you are analyzing an image.
- Do not use phrases such as "This image shows",
  "The image captures", or "In this image".
- Do not use Markdown.
- Do not repeat the same information unnecessarily.

TITLE RULES:

- Clearly identify the primary subject.
- Keep it concise.
- Make it natural and professional.
- Do not introduce facts that are not visible.
- Do not use clickbait.
- The title must be directly related to the uploaded image.

SHORT DESCRIPTION RULES:

- Write 1-2 sentences.
- Summarize the primary subject and its clearly visible surroundings.
- Mention specific visible elements when useful.
- Do not add assumptions.
- The short description must clearly match the title and image.

LONG DESCRIPTION RULES:

- Write 2-3 paragraphs.
- Describe the primary subject first.
- Then describe the surrounding visible elements.
- Include useful details about foreground, background, colors,
  textures, shapes, and composition.
- Keep the entire description focused on what is actually visible.
- Do not turn the description into a fictional story.
- Avoid generic filler.
- Do not introduce a location or context that is not visible.
- Do not repeat the short description word-for-word.

CONTENT CONSISTENCY:

The title, short description, and long description must describe
the SAME primary subject.

For example, if the image contains a waterfall:

GOOD:
Title: "Waterfall Flowing Through a Green Forest"

Short description:
"A waterfall descends over a rocky cliff surrounded by green
ferns, rocks, and dense vegetation."

BAD:
Title: "Exploring a Famous Mountain Destination"

The BAD example introduces information that cannot be verified
from the image.

QUALITY CHECK:

Before returning the result, verify all of the following:

1. Does the title describe the actual primary subject?
2. Does the short description match the image?
3. Does the long description match the image?
4. Does every important claim have visual support?
5. Did you accidentally invent a location?
6. Did you accidentally invent a species?
7. Did you accidentally invent weather or climate?
8. Did you accidentally invent history or cultural information?
9. Are all three fields describing the SAME subject?
10. Is the content specific to THIS image rather than a generic blog?
11. Is the content natural and readable?
12. Remove anything that cannot be confidently supported by the image.

If something cannot be confidently identified, describe it using
a simple generic term.

Return ONLY valid JSON using exactly this structure:

{
    "title": "Title based on the visible subject",
    "short_description": "Short description based on visible details",
    "description": "Detailed description based only on visible details"
}
""",
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:{mime_type};base64,{image_data}"},
                    },
                ],
            }
        ],
    )

    result = response.choices[0].message.content

    return json.loads(result)


if __name__ == "__main__":
    image_path = input("Enter image path: ").strip()

    blog = generate_blog_from_image(image_path)

    print("\nGenerated Blog:\n")

    print(json.dumps(blog, indent=4, ensure_ascii=False))
