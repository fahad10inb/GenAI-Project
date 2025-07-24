# =====================================
# STREAMLIT HOSTING SETUP
# =====================================

import streamlit as st
import os
from dotenv import load_dotenv
import requests
import transformers
from transformers import pipeline

# Load environment variables (for local development)
load_dotenv()

def get_api_token():
    """
    Get API token from multiple sources for different hosting environments
    Priority: Streamlit Secrets > Environment Variable > User Input
    """
    token = None
    
    # Method 1: Streamlit Secrets (for Streamlit Cloud hosting)
    try:
        token = st.secrets["HUGGINGFACEHUB_API_TOKEN"]
        st.sidebar.success("🔒 Token loaded from Streamlit Secrets")
        return token
    except:
        pass
    
    # Method 2: Environment Variable (for Heroku, Railway, etc.)
    token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
    if token:
        st.sidebar.success("🔒 Token loaded from Environment")
        return token
    
    # Method 3: User Input (fallback for development)
    st.sidebar.warning("⚠️ No token found in secrets or environment")
    st.sidebar.markdown("### 🔑 Enter API Token")
    
    token = st.sidebar.text_input(
        "HuggingFace API Token:",
        type="password",
        placeholder="hf_...",
        help="Get from: https://huggingface.co/settings/tokens"
    )
    
    if token:
        st.sidebar.success("✅ Token entered manually")
        return token
    else:
        st.sidebar.error("❌ Please provide an API token")
        st.stop()

# =====================================
# MAIN APPLICATION CODE
# =====================================

def img2txt(image_path):
    """Convert image to text description"""
    try:
        pipe = pipeline("image-to-text", model="Salesforce/blip-image-captioning-base")
        text = pipe(image_path)[0]['generated_text']
        return text
    except Exception as e:
        st.error(f"Image processing error: {str(e)}")
        return None

def generate_story(scenario):
    """Generate story from image description"""
    try:
        intro = "Write a meaningful story in about 300 words about "
        full_prompt = f"{intro} {scenario}"
        
        pipe = transformers.pipeline("text-generation", model="gpt2")
        output = pipe(full_prompt, num_return_sequences=1, max_length=300, truncation=True)
        generated_story = output[0]['generated_text']
        story = generated_story[len(intro):].strip()
        
        return story
    except Exception as e:
        st.error(f"Story generation error: {str(e)}")
        return None

def text_to_speech(message, token):
    """Convert text to speech using HuggingFace API with multiple model fallbacks"""
    
    # List of TTS models to try (in order of preference)
    tts_models = [
        "microsoft/speecht5_tts",
        "facebook/mms-tts-eng",
        "suno/bark-small",
        "espnet/kan-bayashi_ljspeech_vits"
    ]
    
    for i, model in enumerate(tts_models):
        API_URL = f"https://api-inference.huggingface.co/models/{model}"
        headers = {"Authorization": f"Bearer {token}"}
        payload = {"inputs": message}
        
        try:
            st.info(f"🔄 Trying TTS model {i+1}/{len(tts_models)}: {model.split('/')[-1]}")
            response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                # Check if response is audio data
                content_type = response.headers.get('content-type', '')
                
                if 'audio' in content_type or len(response.content) > 1000:
                    # Save audio file
                    audio_filename = 'generated_audio.wav'
                    with open(audio_filename, 'wb') as file:
                        file.write(response.content)
                    
                    st.success(f"✅ Audio generated using {model}")
                    return True
                
                elif 'application/json' in content_type:
                    error_data = response.json()
                    if 'error' in error_data:
                        st.warning(f"⚠️ Model {model}: {error_data['error']}")
                        continue
            
            elif response.status_code == 401:
                st.error("❌ Invalid API token. Please check your token.")
                return False
                
            elif response.status_code == 404:
                st.warning(f"⚠️ Model not found: {model}")
                continue
                
            elif response.status_code == 503:
                st.warning(f"⏳ Model loading: {model}")
                continue
                
            else:
                st.warning(f"⚠️ Error {response.status_code} with {model}")
                continue
                
        except requests.exceptions.Timeout:
            st.warning(f"⏳ Timeout with {model}")
            continue
        except Exception as e:
            st.warning(f"⚠️ Error with {model}: {str(e)}")
            continue
    
    # If all models fail, offer alternatives
    st.error("❌ All TTS models failed. Trying alternative approach...")
    return try_alternative_tts(message, token)

def try_alternative_tts(message, token):
    """Try alternative TTS approach using different API format"""
    try:
        # Try Google Translate TTS-like model
        API_URL = "https://api-inference.huggingface.co/models/facebook/fastspeech2-en-ljspeech"
        headers = {"Authorization": f"Bearer {token}"}
        
        # Some models expect different input format
        payload = {
            "inputs": message,
            "parameters": {
                "normalize": True,
                "phonemize": True,
                "length_scale": 1.0
            }
        }
        
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200 and len(response.content) > 1000:
            with open('generated_audio.wav', 'wb') as file:
                file.write(response.content)
            st.success("✅ Audio generated using alternative method")
            return True
        
    except Exception as e:
        st.warning(f"Alternative TTS also failed: {str(e)}")
    
    # Final fallback - show text and suggest manual TTS
    st.error("❌ Could not generate audio. Here's your story text:")
    st.text_area("Copy this text to any TTS service:", message, height=150)
    
    st.markdown("""
    **Alternative TTS Services:**
    - [Google Text-to-Speech](https://cloud.google.com/text-to-speech)
    - [Amazon Polly](https://aws.amazon.com/polly/)
    - [Natural Readers](https://www.naturalreaders.com/)
    - [TTSMaker](https://ttsmaker.com/)
    """)
    
    return False

def main():
    # Page configuration
    st.set_page_config(
        page_title="Image to Audio Story",
        page_icon="🎵",
        layout="wide"
    )
    
    # Title and description
    st.title("🎵 Image to Audio Story Generator")
    st.markdown("Upload an image and get an AI-generated audio story!")
    
    # Get API token
    api_token = get_api_token()
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Choose an image file",
        type=['jpg', 'jpeg', 'png'],
        help="Upload an image to generate a story"
    )
    
    if uploaded_file is not None:
        # Display uploaded image
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
        
        with col2:
            # Save uploaded file temporarily
            with open(uploaded_file.name, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Process the image
            with st.spinner("🔍 Analyzing image..."):
                scenario = img2txt(uploaded_file.name)
            
            if scenario:
                st.success("✅ Image analyzed!")
                st.write("**Description:**", scenario)
                
                # Generate story
                with st.spinner("📝 Creating story..."):
                    story = generate_story(scenario)
                
                if story:
                    st.success("✅ Story generated!")
                    
                    # Display story
                    with st.expander("📖 View Story", expanded=True):
                        st.write(story)
                    
                    # Generate audio
                    with st.spinner("🎤 Converting to audio..."):
                        audio_success = text_to_speech(story, api_token)
                    
                    if audio_success:
                        st.success("✅ Audio generated!")
                        
                        # Play audio
                        audio_file_path = 'generated_audio.wav'
                        if os.path.exists(audio_file_path):
                            with open(audio_file_path, 'rb') as audio_file:
                                audio_bytes = audio_file.read()
                                st.audio(audio_bytes, format='audio/wav')
                            
                            # Download button
                            st.download_button(
                                label="📥 Download Audio",
                                data=audio_bytes,
                                file_name="story_audio.wav",
                                mime="audio/wav"
                            )
            
            # Cleanup temporary file
            try:
                os.remove(uploaded_file.name)
            except:
                pass
    
    # Instructions in sidebar
    with st.sidebar:
        st.markdown("### 📋 Instructions")
        st.markdown("""
        1. Upload an image (JPG, PNG)
        2. Wait for AI to analyze it
        3. Get your generated story
        4. Listen to the audio version
        5. Download if you like it!
        """)
        
        st.markdown("### 🔧 Hosting Platforms")
        st.markdown("""
        - **Streamlit Cloud**: Uses secrets.toml
        - **Heroku**: Uses environment variables
        - **Railway**: Uses environment variables
        - **Render**: Uses environment variables
        """)

if __name__ == '__main__':
    main()
