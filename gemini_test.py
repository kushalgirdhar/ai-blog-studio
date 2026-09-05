import os
import base64

from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

with open("test_image.jpg", "rb") as f:
    image_bytes = f.read()

image_data = base64.b64encode(image_bytes).decode("utf-8")

interaction = client.interactions.create(
    model="gemini-3.8-flash",
    input=[
        {
            "type": "text",
            "text": "Describe this image in detail. Tell me what the main subject is and what information can be safely understood from the image."
        },
        {
            "type": "image",
            "data": image_data,
            "mime_type": "image/jpeg"
        }
    ]
)

print(interaction.output_text)