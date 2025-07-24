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
    """Convert text to speech using HuggingFace API"""
    API_URL = "https://api-inference.huggingface.co/models/espnet/kan-bayashi_ljspeech_vits"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"inputs": message}
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        
        if response.status_code == 401:
            st.error("❌ Invalid API token. Please check your token.")
            return False
        elif response.status_code == 503:
            st.warning("⏳ Model is loading. Try again in a moment.")
            return False
        elif response.status_code != 200:
            st.error(f"API Error: {response.status_code}")
            return False
        
        # Check content type
        content_type = response.headers.get('content-type', '')
        if 'application/json' in content_type:
            error_data = response.json()
            st.warning(f"Model not ready: {error_data.get('error', 'Try again later')}")
            return False
        
        # Save audio file
        with open('generated_audio.flac', 'wb') as file:
            file.write(response.content)
        
        return True
        
    except Exception as e:
        st.error(f"TTS Error: {str(e)}")
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
                        with open('generated_audio.flac', 'rb') as audio_file:
                            audio_bytes = audio_file.read()
                            st.audio(audio_bytes, format='audio/flac')
                        
                        # Download button
                        st.download_button(
                            label="📥 Download Audio",
                            data=audio_bytes,
                            file_name="story_audio.flac",
                            mime="audio/flac"
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
