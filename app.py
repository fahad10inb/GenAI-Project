from dotenv import find_dotenv, load_dotenv
from langchain import OpenAI, PromptTemplate, LLMChain
import requests
import os
import transformers
from transformers import pipeline
import streamlit as st

load_dotenv(find_dotenv())
HUGGINGFACEHUB_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")

def img2txt(url):
    try:
        pipe = pipeline("image-to-text", model="Salesforce/blip-image-captioning-base")
        text = pipe(url)[0]['generated_text']
        print(text)
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

def text_speech(message):
    # Check if API token exists
    if not HUGGINGFACEHUB_API_TOKEN:
        st.error("Hugging Face API token not found. Please check your .env file.")
        return False
    
    API_URL = "https://api-inference.huggingface.co/models/espnet/kan-bayashi_ljspeech_vits"
    headers = {"Authorization": f"Bearer {HUGGINGFACEHUB_API_TOKEN}"}
    payload = {"inputs": message}
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        
        # Check response status
        if response.status_code == 401:
            st.error("Authentication failed. Please check your Hugging Face API token.")
            return False
        elif response.status_code == 503:
            st.warning("Model is loading. Please try again in a few moments.")
            return False
        elif response.status_code != 200:
            st.error(f"API request failed with status {response.status_code}: {response.text}")
            return False
        
        # Check if response content is valid
        if response.headers.get('content-type', '').startswith('application/json'):
            # Model might still be loading
            error_data = response.json()
            if 'error' in error_data:
                st.warning(f"Model error: {error_data['error']}")
                return False
        
        # Save audio file with consistent naming
        audio_filename = 'audio.flac'
        with open(audio_filename, 'wb') as file:
            file.write(response.content)
        
        return True
        
    except requests.exceptions.RequestException as e:
        st.error(f"Network error: {str(e)}")
        return False
    except Exception as e:
        st.error(f"Error in text-to-speech: {str(e)}")
        return False

def main():
    st.set_page_config(page_title="IMAGE TO AUDIO", page_icon="🎵")

    st.header("Turn Image into an Audio Story")
    
    # Add instructions for API token
    if not HUGGINGFACEHUB_API_TOKEN:
        st.warning("⚠️ Please set your HUGGINGFACEHUB_API_TOKEN in your .env file")
        st.info("Get your token from: https://huggingface.co/settings/tokens")

    uploaded_file = st.file_uploader("Upload an Image...", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()

        with open(uploaded_file.name, "wb") as file:
            file.write(bytes_data)

        st.image(uploaded_file, caption="Uploaded Image..", use_column_width=True)

        with st.spinner("Analyzing image..."):
            scenario = img2txt(uploaded_file.name)
        
        if scenario:
            with st.spinner("Generating story..."):
                story = generate_story(scenario)
            
            if story:
                with st.spinner("Converting to speech..."):
                    success = text_speech(story)

                with st.expander("Situation"):
                    st.write(scenario)

                with st.expander("Story"):
                    st.write(story)

                if success:
                    st.audio("audio.flac")  # Fixed filename case
                else:
                    st.error("Failed to generate audio. Please try again.")

        # Clean up uploaded file
        try:
            os.remove(uploaded_file.name)
        except:
            pass

if __name__ == '__main__':
    main()
