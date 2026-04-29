from gtts import gTTS
import os

def generate_voiceover(text: str, save_path: str, lang: str = "en") -> str:
    """
    Generate voiceover MP3 using Google TTS (free).
    Returns path to saved audio file.
    """
    tts = gTTS(text=text, lang=lang, slow=False)
    tts.save(save_path)
    return save_path


def generate_all_voiceovers(scenes: list[dict], output_dir: str, lang: str = "en") -> list[str]:
    """
    Generate voiceovers for all scenes. Returns list of audio paths.
    """
    os.makedirs(output_dir, exist_ok=True)
    audio_paths = []
    
    for i, scene in enumerate(scenes):
        save_path = os.path.join(output_dir, f"audio_{i}.mp3")
        generate_voiceover(scene["narration"], save_path, lang=lang)
        audio_paths.append(save_path)
    
    return audio_paths
