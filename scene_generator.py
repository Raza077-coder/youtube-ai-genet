import google.generativeai as genai
import json
import re
import os

def generate_scenes(prompt: str, num_scenes: int = 4) -> list[dict]:
    """
    Takes a topic/prompt and returns list of scenes.
    Each scene: {title, narration, image_prompt}
    Uses Gemini API (free, no credit card needed)
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    genai.configure(api_key=api_key)
    
    model = genai.GenerativeModel("gemini-1.5-flash")  # free tier model

    system_prompt = f"""You are a YouTube video script writer.
Given a topic, generate exactly {num_scenes} scenes for a short video.
Return ONLY valid JSON. No markdown, no explanation, no code fences.
Format:
{{
  "scenes": [
    {{
      "title": "Scene title (short)",
      "narration": "Voiceover text for this scene (2-3 sentences max)",
      "image_prompt": "Detailed visual description for AI image generation (cinematic, detailed)"
    }}
  ]
}}

Topic: {prompt}
Generate {num_scenes} scenes."""

    response = model.generate_content(system_prompt)
    raw = response.text.strip()

    # Strip markdown code fences if present
    raw = re.sub(r"```json|```", "", raw).strip()

    data = json.loads(raw)
    return data["scenes"]
