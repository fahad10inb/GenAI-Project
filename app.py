import streamlit as st
import os
from dotenv import load_dotenv
import requests
import transformers
from transformers import pipeline
import pyttsx3  # Simple offline TTS
import io
import base64

load_dotenv()

def get_api_token():
    """Get API token securely"""
    try:
        token = st.secrets["HUGGINGFACEHUB_API_TOKEN"]
        return token
    except:
        pass
    
    token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
    if token:
        return token
    
    token = st.sidebar.text_input(
        "HuggingFace API Token:",
        type="password",
        placeholder="hf_...",
    )
    return token

def img2txt(image_path):
    """Convert image to text"""
    try:
        pipe = pipeline("image-to-text", model="Salesforce/blip-image-captioning-base")
        text = pipe(image_path)[0]['generated_text']
        return text
    except Exception as e:
        st.error(f"Image processing error: {str(e)}")
        return None

def generate_story(scenario):
    """Generate story from scenario"""
    try:
        intro = "Write a short meaningful story about "
        full_prompt = f"{intro} {scenario}"
        
        pipe = transformers.pipeline("text-generation", model="gpt2")
        output = pipe(full_prompt, num_return_sequences=1, max_length=200, truncation=True)
        story = output[0]['generated_text'][len(intro):].strip()
        
        return story
    except Exception as e:
        st.error(f"Story generation error: {str(e)}")
        return None

# SIMPLE WORKING TTS OPTIONS

def browser_tts(text):
    """Use browser's built-in speech synthesis (JavaScript)"""
    # Create HTML with JavaScript for TTS
    html_code = f"""
    <div>
        <button onclick="speakText()" style="
            background: #ff4b4b;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
        ">🔊 Play Audio</button>
        
        <button onclick="stopSpeech()" style="
            background: #666;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            margin-left: 10px;
        ">⏹️ Stop</button>
    </div>
    
    <script>
        function speakText() {{
            const text = `{text}`;
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.rate = 0.8;
            utterance.pitch = 1;
            utterance.volume = 1;
            speechSynthesis.speak(utterance);
        }}
        
        function stopSpeech() {{
            speechSynthesis.cancel();
        }}
    </script>
    """
    return html_code

def google_translate_tts(text):
    """Use Google Translate TTS (simple and reliable)"""
    try:
        # This is a simple approach using gTTS if available
        from gtts import gTTS
        import tempfile
        
        # Create TTS object
        tts = gTTS(text=text, lang='en', slow=False)
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
            tts.save(tmp_file.name)
            return tmp_file.name
            
    except ImportError:
        st.warning("gTTS not installed. Install with: pip install gtts")
        return None
    except Exception as e:
        st.error(f"gTTS error: {str(e)}")
        return None

def edge_tts_simple(text):
    """Use Microsoft Edge TTS (if available)"""
    try:
        import edge_tts
        import asyncio
        import tempfile
        
        async def generate_speech():
            communicate = edge_tts.Communicate(text, "en-US-AriaNeural")
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                async for chunk in communicate.stream():
                    if chunk["type"] == "audio":
                        tmp_file.write(chunk["data"])
                return tmp_file.name
        
        # Run async function
        audio_file = asyncio.run(generate_speech())
        return audio_file
        
    except ImportError:
        st.warning("edge-tts not installed. Install with: pip install edge-tts")
        return None
    except Exception as e:
        st.error(f"Edge TTS error: {str(e)}")
        return None

def main():
    st.set_page_config(page_title="Image to Audio Story", page_icon="🎵")
    st.title("🎵 Image to Audio Story Generator")
    
    # Get token
    token = get_api_token()
    if not token:
        st.warning("Please provide your HuggingFace API token")
        st.stop()
    
    # File upload
    uploaded_file = st.file_uploader("Upload an image", type=['jpg', 'jpeg', 'png'])
    
    if uploaded_file:
        # Save and display image
        with open(uploaded_file.name, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.image(uploaded_file, caption="Your Image", use_column_width=True)
        
        with col2:
            # Process image
            with st.spinner("🔍 Analyzing image..."):
                scenario = img2txt(uploaded_file.name)
            
            if scenario:
                st.success("✅ Image analyzed!")
                st.write("**Description:**", scenario)
                
                # Generate story
                with st.spinner("📝 Writing story..."):
                    story = generate_story(scenario)
                
                if story:
                    st.success("✅ Story created!")
                    
                    # Show story
                    st.subheader("📖 Your Story")
                    st.write(story)
                    
                    # TTS OPTIONS
                    st.subheader("🔊 Audio Options")
                    
                    # Option 1: Browser TTS (Always works)
                    st.markdown("**Option 1: Browser Speech (Instant)**")
                    browser_html = browser_tts(story)
                    st.components.v1.html(browser_html, height=100)
                    
                    # Option 2: Download options
                    st.markdown("**Option 2: Generate Audio File**")
                    
                    col_a, col_b = st.columns(2)
                    
                    with col_a:
                        if st.button("🎵 Generate with Google TTS"):
                            audio_file = google_translate_tts(story)
                            if audio_file:
                                with open(audio_file, 'rb') as f:
                                    audio_bytes = f.read()
                                st.audio(audio_bytes, format='audio/mp3')
                                st.download_button(
                                    "📥 Download Audio",
                                    audio_bytes,
                                    "story.mp3",
                                    "audio/mp3"
                                )
                                os.unlink(audio_file)  # Clean up
                    
                    with col_b:
                        if st.button("🎤 Generate with Edge TTS"):
                            audio_file = edge_tts_simple(story)
                            if audio_file:
                                with open(audio_file, 'rb') as f:
                                    audio_bytes = f.read()
                                st.audio(audio_bytes, format='audio/mp3')
                                st.download_button(
                                    "📥 Download Audio",
                                    audio_bytes,
                                    "story_edge.mp3",
                                    "audio/mp3"
                                )
                                os.unlink(audio_file)  # Clean up
                    
                    # Option 3: Manual alternatives
                    st.markdown("**Option 3: Copy Text for External TTS**")
                    with st.expander("📋 Copy Story Text"):
                        st.text_area("Story Text:", story, height=100)
                        st.markdown("""
                        **Quick TTS Services:**
                        - [NaturalReaders](https://www.naturalreaders.com/online/)
                        - [TTSMaker](https://ttsmaker.com/)
                        - [Text to Speech Online](https://www.texttospeechonline.com/)
                        """)
        
        # Cleanup
        try:
            os.remove(uploaded_file.name)
        except:
            pass
    
    # Installation instructions
    with st.sidebar:
        st.markdown("### 📦 For Better Audio Quality")
        st.code("pip install gtts edge-tts", language="bash")
        st.markdown("""
        **Browser TTS**: Works immediately, no installation needed
        
        **Google TTS**: Better quality, requires `gtts` package
        
        **Edge TTS**: Best quality, requires `edge-tts` package
        """)

if __name__ == '__main__':
    main()
