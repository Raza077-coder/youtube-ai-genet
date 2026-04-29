from moviepy.editor import (
    ImageClip, AudioFileClip, concatenate_videoclips, 
    CompositeVideoClip, TextClip, ColorClip
)
from moviepy.video.fx.all import resize
import numpy as np
from PIL import Image
import os

VIDEO_W = 1280
VIDEO_H = 720
FPS = 24


def zoom_in_effect(clip, zoom_ratio=0.04):
    """Apply slow zoom-in (Ken Burns effect)."""
    def effect(get_frame, t):
        img = get_frame(t)
        duration = clip.duration
        # Zoom from 1.0 to 1.0 + zoom_ratio
        zoom = 1 + zoom_ratio * (t / duration)
        
        h, w = img.shape[:2]
        new_h, new_w = int(h * zoom), int(w * zoom)
        
        # Resize
        pil_img = Image.fromarray(img)
        pil_img = pil_img.resize((new_w, new_h), Image.LANCZOS)
        img_zoomed = np.array(pil_img)
        
        # Center crop back to original size
        start_y = (new_h - h) // 2
        start_x = (new_w - w) // 2
        return img_zoomed[start_y:start_y+h, start_x:start_x+w]
    
    return clip.fl(effect)


def pan_right_effect(clip, pan_ratio=0.03):
    """Apply slow pan from left to right."""
    def effect(get_frame, t):
        img = get_frame(t)
        duration = clip.duration
        progress = t / duration  # 0 to 1
        
        h, w = img.shape[:2]
        # Expand width, pan horizontally
        new_w = int(w * (1 + pan_ratio))
        
        pil_img = Image.fromarray(img)
        pil_img = pil_img.resize((new_w, h), Image.LANCZOS)
        img_panned = np.array(pil_img)
        
        # Shift crop position based on time
        max_shift = new_w - w
        start_x = int(max_shift * progress)
        return img_panned[:, start_x:start_x+w]
    
    return clip.fl(effect)


def add_subtitle_overlay(clip, text: str, duration: float):
    """Add subtitle text overlay at bottom of clip."""
    try:
        txt_clip = (TextClip(text, 
                             fontsize=32, 
                             color='white',
                             font='Arial-Bold',
                             stroke_color='black',
                             stroke_width=2,
                             size=(VIDEO_W - 60, None),
                             method='caption')
                    .set_duration(duration)
                    .set_position(('center', VIDEO_H - 100)))
        
        return CompositeVideoClip([clip, txt_clip])
    except Exception:
        # If subtitle fails (font issue), return clip without subtitle
        return clip


def create_scene_clip(image_path: str, audio_path: str, 
                      narration: str, scene_index: int,
                      add_subtitles: bool = True) -> ImageClip:
    """
    Create a single scene clip: image + animation + audio + optional subtitle.
    """
    # Load audio to get duration
    audio_clip = AudioFileClip(audio_path)
    duration = audio_clip.duration + 0.5  # small buffer
    
    # Create image clip
    img_clip = ImageClip(image_path).set_duration(duration)
    img_clip = img_clip.resize((VIDEO_W, VIDEO_H))
    
    # Alternate between zoom and pan for variety
    if scene_index % 2 == 0:
        img_clip = zoom_in_effect(img_clip)
    else:
        img_clip = pan_right_effect(img_clip)
    
    # Add subtitles if requested
    if add_subtitles:
        img_clip = add_subtitle_overlay(img_clip, narration, duration)
    
    # Attach audio
    final_clip = img_clip.set_audio(audio_clip)
    return final_clip


def create_final_video(scenes: list[dict], 
                       image_paths: list[str], 
                       audio_paths: list[str],
                       output_path: str,
                       add_subtitles: bool = True) -> str:
    """
    Combine all scenes into final MP4 video.
    Returns path to output video.
    """
    clips = []
    
    for i, (scene, img_path, audio_path) in enumerate(zip(scenes, image_paths, audio_paths)):
        clip = create_scene_clip(
            image_path=img_path,
            audio_path=audio_path,
            narration=scene["narration"],
            scene_index=i,
            add_subtitles=add_subtitles
        )
        clips.append(clip)
    
    # Concatenate all scenes
    final = concatenate_videoclips(clips, method="compose")
    
    # Export
    final.write_videofile(
        output_path,
        fps=FPS,
        codec="libx264",
        audio_codec="aac",
        temp_audiofile="temp_audio.m4a",
        remove_temp=True,
        verbose=False,
        logger=None
    )
    
    # Cleanup clips
    for clip in clips:
        clip.close()
    final.close()
    
    return output_path
