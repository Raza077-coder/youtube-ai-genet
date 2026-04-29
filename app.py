import streamlit as st
import os
import shutil
import tempfile
import time
from scene_generator import generate_scenes
from image_generator import generate_all_images
from tts_generator import generate_all_voiceovers
from video_creator import create_final_video

# ─── Page Config ──────────────────────────────────────────────
st.set_page_config(
    page_title="AI YouTube Video Generator",
    page_icon="🎬",
    layout="wide"
)

# ─── CSS ──────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] { font-family: 'Space Grotesk', sans-serif; }
    
    .main-header {
        text-align: center;
        padding: 2rem 0 1rem 0;
    }
    .main-header h1 {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #FF6B6B, #FFE66D, #4ECDC4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .main-header p {
        color: #888;
        font-size: 1.1rem;
    }
    
    .feature-badge {
        display: inline-block;
        background: #1a1a2e;
        border: 1px solid #333;
        border-radius: 20px;
        padding: 4px 14px;
        font-size: 0.8rem;
        color: #aaa;
        margin: 3px;
    }
    
    .scene-card {
        background: #0f0f1a;
        border: 1px solid #222;
        border-radius: 12px;
        padding: 1.2rem;
        margin: 0.6rem 0;
    }
    
    .scene-number {
        color: #FFE66D;
        font-weight: 700;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .scene-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #fff;
        margin: 4px 0;
    }
    
    .scene-narration {
        color: #bbb;
        font-size: 0.9rem;
        line-height: 1.5;
    }
    
    .stProgress > div > div { background: linear-gradient(90deg, #FF6B6B, #FFE66D); }
    
    .stButton > button {
        background: linear-gradient(135deg, #FF6B6B, #FF8E53);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        font-size: 1rem;
        padding: 0.6rem 2rem;
        transition: all 0.2s;
    }
    
    .stButton > button:hover { transform: translateY(-1px); box-shadow: 0 4px 15px rgba(255,107,107,0.4); }
    
    div[data-testid="stExpander"] { border: 1px solid #222; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# ─── Header ───────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🎬 AI Video Generator</h1>
    <p>Turn any topic into a YouTube-ready video in minutes</p>
    <div style="margin-top: 1rem;">
        <span class="feature-badge">✨ AI Scenes</span>
        <span class="feature-badge">🖼️ Auto Images</span>
        <span class="feature-badge">🎙️ Voiceover</span>
        <span class="feature-badge">🎞️ Animations</span>
        <span class="feature-badge">📥 MP4 Export</span>
    </div>
</div>
""", unsafe_allow_html=True)

st.divider()

# ─── Sidebar Settings ─────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    
    num_scenes = st.slider("Number of Scenes", min_value=2, max_value=6, value=4)
    
    tts_language = st.selectbox("Voice Language", 
                                 options=["en", "ur", "hi", "ar", "fr", "de", "es"],
                                 format_func=lambda x: {
                                     "en": "🇬🇧 English",
                                     "ur": "🇵🇰 Urdu",
                                     "hi": "🇮🇳 Hindi",
                                     "ar": "🇸🇦 Arabic",
                                     "fr": "🇫🇷 French",
                                     "de": "🇩🇪 German",
                                     "es": "🇪🇸 Spanish"
                                 }[x])
    
    add_subtitles = st.toggle("Add Subtitles", value=True)
    
    st.divider()
    st.markdown("### ℹ️ About")
    st.markdown("""
    **Free tools used:**
    - 🤖 Claude AI (scene writing)
    - 🖼️ Pollinations.ai (images)  
    - 🎙️ Google TTS (voice)
    - 🎬 MoviePy (video)
    """)
    
    st.markdown("### ⚠️ Limitations")
    st.markdown("""
    - Image quality: Medium (free tier)
    - No lip sync
    - No background music
    - Long videos = longer wait
    """)

# ─── Main Input ───────────────────────────────────────────────
col1, col2 = st.columns([3, 1])

with col1:
    prompt = st.text_area(
        "📝 Enter your video topic or script idea",
        placeholder="e.g., 'The history of artificial intelligence' or 'How black holes work' or 'Top 5 tips for productivity'",
        height=120
    )

with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    generate_btn = st.button("🚀 Generate Video", use_container_width=True)

# ─── Example Prompts ──────────────────────────────────────────
with st.expander("💡 Example Prompts"):
    examples = [
        "The history of artificial intelligence and how it changed the world",
        "How black holes form and what happens if you fall into one",
        "Top 5 productivity hacks used by successful people",
        "The science behind climate change explained simply",
        "How social media is affecting mental health of teenagers",
    ]
    cols = st.columns(2)
    for i, ex in enumerate(examples):
        with cols[i % 2]:
            if st.button(f"📌 {ex[:45]}...", key=f"ex_{i}", use_container_width=True):
                st.session_state["example_prompt"] = ex
                st.rerun()

# Handle example selection
if "example_prompt" in st.session_state and not prompt:
    prompt = st.session_state["example_prompt"]

# ─── Generation Pipeline ──────────────────────────────────────
if generate_btn and prompt.strip():
    
    # Create temp working directory
    work_dir = tempfile.mkdtemp(prefix="aivid_")
    images_dir = os.path.join(work_dir, "images")
    audio_dir = os.path.join(work_dir, "audio")
    output_video = os.path.join(work_dir, "output.mp4")
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # ── Step 1: Generate Scenes ────────────────────────────
        status_text.markdown("**Step 1/4** — 🧠 AI is writing your video script...")
        progress_bar.progress(10)
        
        scenes = generate_scenes(prompt, num_scenes=num_scenes)
        
        # Display scenes
        st.markdown("### 📋 Generated Script")
        for i, scene in enumerate(scenes):
            st.markdown(f"""
            <div class="scene-card">
                <div class="scene-number">Scene {i+1}</div>
                <div class="scene-title">{scene['title']}</div>
                <div class="scene-narration">{scene['narration']}</div>
            </div>
            """, unsafe_allow_html=True)
        
        progress_bar.progress(25)
        
        # ── Step 2: Generate Images ────────────────────────────
        status_text.markdown(f"**Step 2/4** — 🖼️ Generating {len(scenes)} images (this takes ~1-2 min)...")
        progress_bar.progress(30)
        
        image_paths = generate_all_images(scenes, images_dir)
        
        # Show generated images
        st.markdown("### 🖼️ Generated Scenes")
        img_cols = st.columns(min(len(scenes), 4))
        for i, img_path in enumerate(image_paths):
            with img_cols[i % len(img_cols)]:
                st.image(img_path, caption=scenes[i]["title"], use_column_width=True)
        
        progress_bar.progress(55)
        
        # ── Step 3: Generate Voiceovers ────────────────────────
        status_text.markdown("**Step 3/4** — 🎙️ Generating voiceovers...")
        progress_bar.progress(60)
        
        audio_paths = generate_all_voiceovers(scenes, audio_dir, lang=tts_language)
        
        progress_bar.progress(70)
        
        # ── Step 4: Create Video ───────────────────────────────
        status_text.markdown("**Step 4/4** — 🎬 Combining into video (longest step)...")
        progress_bar.progress(75)
        
        create_final_video(
            scenes=scenes,
            image_paths=image_paths,
            audio_paths=audio_paths,
            output_path=output_video,
            add_subtitles=add_subtitles
        )
        
        progress_bar.progress(100)
        status_text.markdown("✅ **Video ready!**")
        
        # ── Download ───────────────────────────────────────────
        st.markdown("### 📥 Download Your Video")
        
        with open(output_video, "rb") as f:
            video_bytes = f.read()
        
        # Preview
        st.video(output_video)
        
        # Download button
        safe_name = prompt[:30].replace(" ", "_").lower()
        st.download_button(
            label="⬇️ Download MP4",
            data=video_bytes,
            file_name=f"ai_video_{safe_name}.mp4",
            mime="video/mp4",
            use_container_width=True
        )
        
        st.success(f"🎉 Video created! {len(scenes)} scenes, {tts_language.upper()} voiceover.")
        
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        st.markdown("**Common fixes:**")
        st.markdown("- Check your `ANTHROPIC_API_KEY` in `.env`")
        st.markdown("- Pollinations.ai might be slow — try again in a minute")
        st.markdown("- Make sure ffmpeg is installed: `sudo apt install ffmpeg`")
    
    finally:
        # Cleanup temp files (but output video already read into memory)
        try:
            shutil.rmtree(work_dir, ignore_errors=True)
        except Exception:
            pass

elif generate_btn and not prompt.strip():
    st.warning("⚠️ Please enter a topic first.")
