# Method 1: Using .env file (RECOMMENDED)
from dotenv import load_dotenv
import os
import streamlit as st

# Load environment variables
load_dotenv()

def get_hf_token():
    """Safely get HuggingFace token"""
    token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
    if not token:
        st.error("❌ HuggingFace API token not found!")
        st.info("Please add HUGGINGFACEHUB_API_TOKEN to your .env file")
        st.stop()
    return token

# Usage in your app
HUGGINGFACEHUB_API_TOKEN = get_hf_token()

# =====================================
# Method 2: Using Streamlit Secrets (CLOUD DEPLOYMENT)
# =====================================

def get_hf_token_from_secrets():
    """Get token from Streamlit secrets (for cloud deployment)"""
    try:
        return st.secrets["HUGGINGFACEHUB_API_TOKEN"]
    except KeyError:
        st.error("❌ Token not found in Streamlit secrets!")
        st.info("Add your token to .streamlit/secrets.toml")
        st.stop()

# =====================================
# Method 3: User Input (DEVELOPMENT ONLY)
# =====================================

def get_hf_token_from_input():
    """Allow user to input token (development only)"""
    token = st.sidebar.text_input(
        "Enter HuggingFace API Token", 
        type="password",
        help="Get your token from https://huggingface.co/settings/tokens"
    )
    
    if not token:
        st.warning("⚠️ Please enter your HuggingFace API token in the sidebar")
        st.stop()
    
    return token

# =====================================
# COMPLETE UPDATED APP WITH SECURE TOKEN
# =====================================

from dotenv import find_dotenv, load_dotenv
import requests
import transformers
from transformers import pipeline

load_dotenv(find_dotenv())

def get_secure_token():
    """Get token securely with multiple fallback methods"""
    # Method 1: Environment variable
    token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
    
    # Method 2: Streamlit secrets (for cloud)
    if not token:
        try:
            token = st.secrets["HUGGINGFACEHUB_API_TOKEN"]
        except:
            pass
    
    # Method 3: User input (development only)
    if not token:
        st.sidebar.markdown("### 🔑 API Configuration")
        token = st.sidebar.text_input(
            "HuggingFace API Token", 
            type="password",
            help="Get from: https://huggingface.co/settings/tokens"
        )
    
    if not token:
        st.error("❌ No API token provided!")
        st.markdown("""
        **To fix this:**
        1. Get a token from: https://huggingface.co/settings/tokens
        2. Add it to your `.env` file: `HUGGINGFACEHUB_API_TOKEN=your_token_here`
        3. Or enter it in the sidebar
        """)
        st.stop()
    
    return token

def img2txt(url):
    try:
        pipe = pipeline("image-to-text", model="Salesforce/blip-image-captioning-base")
        text = pipe(url)[0]['generated_text']
        return text
    except Exception as e:
        st.error(f"Error in image captioning: {str(e)}")
        return None

def generate_story(check):
    try:
        intro = "write a meaningful story in about 300 words about "
        full_prompt = f"{intro} {check}"
        
        pipe = transformers.pipeline("text-generation", model="gpt2")
        output = pipe(full_prompt, num_return_sequences=1, max_length=300, truncation=True)
        generated_story = output[0]['generated_text']
        story = generated_story[len(intro):].strip()  
        
        return story
    except Exception as e:
        st.error(f"Error in story generation: {str(e)}")
        return None

def text_speech(message, token):
    API_URL = "https://api-inference.huggingface.co/models/espnet/kan-bayashi_ljspeech_vits"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"inputs": message}
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        
        if response.status_code == 401:
            st.error("❌ Invalid API token. Please check your token.")
            return False
        elif response.status_code == 503:
            st.warning("⏳ Model is loading. Please try again in a few moments.")
            return False
        elif response.status_code != 200:
            st.error(f"API request failed: {response.status_code}")
            return False
        
        # Check if response is JSON (error) or audio data
        content_type = response.headers.get('content-type', '')
        if 'application/json' in content_type:
            error_data = response.json()
            st.error(f"Model error: {error_data.get('error', 'Unknown error')}")
            return False
        
        # Save audio file
        with open('audio.flac', 'wb') as file:
            file.write(response.content)
        
        return True
        
    except Exception as e:
        st.error(f"Error in text-to-speech: {str(e)}")
        return False

def main():
    st.set_page_config(page_title="IMAGE TO AUDIO", page_icon="🎵")
    st.header("🎵 Turn Image into an Audio Story")
    
    # Get token securely
    token = get_secure_token()
    
    # Show token status (masked)
    if token:
        masked_token = f"hf_{'*' * 30}{token[-6:]}"
        st.sidebar.success(f"✅ Token loaded: {masked_token}")
    
    uploaded_file = st.file_uploader(
        "Upload an Image...", 
        type=["jpg", "jpeg", "png"],
        help="Upload an image to generate a story and convert it to audio"
    )

    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        
        with open(uploaded_file.name, "wb") as file:
            file.write(bytes_data)

        st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)

        # Processing pipeline
        with st.spinner("🔍 Analyzing image..."):
            scenario = img2txt(uploaded_file.name)
        
        if scenario:
            with st.spinner("📝 Generating story..."):
                story = generate_story(scenario)
            
            if story:
                with st.spinner("🎤 Converting to speech..."):
                    success = text_speech(story, token)

                # Display results
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("🎯 Image Description")
                    st.write(scenario)
                
                with col2:
                    st.subheader("📖 Generated Story")
                    st.write(story)

                if success:
                    st.subheader("🎵 Audio Story")
                    st.audio("audio.flac")
                    st.success("✅ Audio generated successfully!")
                else:
                    st.error("❌ Failed to generate audio. Please try again.")

        # Cleanup
        try:
            os.remove(uploaded_file.name)
        except:
            pass

if __name__ == '__main__':
    main()
