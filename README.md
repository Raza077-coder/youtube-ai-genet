# 🎬 AI YouTube Video Generator

Turn any topic into a YouTube-ready MP4 video using free AI tools.

## What it does
- Takes your text prompt
- Auto-generates 2–6 scenes using Claude AI
- Creates cinematic images via Pollinations.ai (free)
- Adds voiceover using Google TTS (free)
- Applies zoom/pan animations (Ken Burns effect)
- Exports downloadable MP4

---

## Setup (5 minutes)

### 1. System requirements
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg python3-pip -y

# Windows: Download ffmpeg from https://ffmpeg.org/download.html
# macOS: brew install ffmpeg
```

### 2. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 3. Set your API key
```bash
cp .env.example .env
# Edit .env and add your Anthropic API key
# Get free key at: https://console.anthropic.com
```

### 4. Run the app
```bash
streamlit run app.py
```

Open browser at: `http://localhost:8501`

---

## Free Tier Limits

| Tool | Free Limit |
|------|-----------|
| Claude API | $5 free credit on signup |
| Pollinations.ai | Unlimited (may be slow) |
| Google TTS | Unlimited |
| MoviePy | Unlimited (local) |

---

## Honest Limitations

- **Image quality**: Medium. Free Pollinations uses Flux model — decent but not Midjourney
- **Voiceover**: gTTS sounds robotic. For better quality use ElevenLabs (paid)
- **No lip sync**: Characters don't move
- **No background music**: Can add royalty-free music from Pixabay manually
- **Speed**: ~3-5 min per video (mostly image generation)
- **Long videos**: 10+ scenes will be slow and may hit rate limits

---

## Want Better Quality? (Paid upgrades)

| Feature | Upgrade |
|---------|---------|
| Better images | Stability AI API ($0.003/image) |
| Natural voice | ElevenLabs (~$5/mo) |
| Background music | Add AudioFileClip from royalty-free MP3 |
| Subtitles style | MoviePy TextClip with custom fonts |

---

## Project Structure

```
├── app.py              # Streamlit UI
├── scene_generator.py  # Claude → scenes JSON
├── image_generator.py  # Pollinations.ai → images
├── tts_generator.py    # gTTS → MP3 audio
├── video_creator.py    # MoviePy → MP4
├── requirements.txt
└── .env.example
```
