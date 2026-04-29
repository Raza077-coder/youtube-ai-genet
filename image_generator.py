import requests
import time
from PIL import Image
from io import BytesIO
import os

POLLINATIONS_URL = "https://image.pollinations.ai/prompt/"

def generate_image(prompt: str, width: int = 1280, height: int = 720, save_path: str = None) -> Image.Image:
    """
    Generate image using Pollinations.ai (free, no API key needed).
    Returns PIL Image object.
    """
    # Clean prompt for URL
    clean_prompt = prompt.replace(" ", "%20").replace(",", "%2C")
    
    url = f"{POLLINATIONS_URL}{clean_prompt}?width={width}&height={height}&nologo=true&model=flux"
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=60)
            if response.status_code == 200:
                img = Image.open(BytesIO(response.content)).convert("RGB")
                if save_path:
                    img.save(save_path)
                return img
            else:
                time.sleep(2)
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(3)
            else:
                raise Exception(f"Image generation failed after {max_retries} attempts: {e}")
    
    raise Exception("Image generation failed")


def generate_all_images(scenes: list[dict], output_dir: str) -> list[str]:
    """
    Generate images for all scenes. Returns list of saved image paths.
    """
    os.makedirs(output_dir, exist_ok=True)
    image_paths = []
    
    for i, scene in enumerate(scenes):
        save_path = os.path.join(output_dir, f"scene_{i}.png")
        
        # Add cinematic quality boosters to prompt
        enhanced_prompt = f"{scene['image_prompt']}, cinematic lighting, high quality, 4k, professional photography"
        
        generate_image(enhanced_prompt, save_path=save_path)
        image_paths.append(save_path)
        
        # Rate limit: be nice to free API
        time.sleep(1)
    
    return image_paths
