from dotenv import find_dotenv, load_dotenv
import requests
import os
import transformers
from transformers import pipeline
import streamlit as st
from PIL import Image
import torch

# Load environment variables
load_dotenv(find_dotenv())
HUGGINGFACEHUB_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")

def img2txt(image_path):
    """Convert image to text description"""
    try:
        # Use CPU for better compatibility on Streamlit Cloud
        pipe = pipeline("image-to-text", 
                       model="Salesforce/blip-image-captioning-base",
                       device=-1)  # Force CPU usage
        
        # Open and process the image
        image = Image.open(image_path)
        text = pipe(image)[0]['generated_text']
        print(f"Generated caption: {text}")
        return text
    except Exception as e:
        st.error(f"Error in image captioning: {str(e)}")
        return "A beautiful scene"

def generate_story(scenario):
    """Generate a story based on the scenario"""
    try:
        intro = "Write a meaningful story in about 200 words about"
        full_prompt = f"{intro} {scenario}"
        
        # Use CPU for better compatibility
        pipe = pipeline("text-generation", 
                       model="gpt2",
                       device=-1,  # Force CPU usage
                       pad_token_id=50256)  # Set pad token
        
        output = pipe(full_prompt, 
                     num_return_sequences=1, 
                     max_length=200,  # Reduced for better performance
                     truncation=True,
                     do_sample=True,
                     temperature=0.7)
        
        generated_story = output[0]['generated_text']
        # Remove the intro part from the generated story
        story = generated_story.replace(intro, "").strip()
        
        return story
    except Exception as e:
        st.error(f"Error in story generation: {str(e)}")
        return f"Once upon a time, there was {scenario}. It was a wonderful moment that brought joy to everyone who witnessed it."

def text_to_speech(message):
    """Convert text to speech using Hugging Face API"""
    try:
        if not HUGGINGFACEHUB_API_TOKEN:
            st.error("Hugging Face API token not found. Please set HUGGINGFACEHUB_API_TOKEN in your environment.")
            return False
            
        API_URL = "https://api-inference.huggingface.co/models/espnet/kan-bayashi_ljspeech_vits"
        headers = {"Authorization": f"Bearer {HUGGINGFACEHUB_API_TOKEN}"}
        payload = {"inputs": message}
        
        response = requests.post(API_URL, headers=headers, json=payload)
        
        if response.status_code == 200:
            with open('audio.flac', 'wb') as file:
                file.write(response.content)
            return True
        else:
            st.error(f"API request failed with status code: {response.status_code}")
            return False
    except Exception as e:
        st.error(f"Error in text-to-speech: {str(e)}")
        return False

def main():
    st.set_page_config(page_title="IMAGE TO AUDIO STORY", page_icon="🎵")
    
    st.header("Turn Image into an Audio Story 🎵")
    st.write("Upload an image and I'll create a story about it, then convert it to audio!")
    
    uploaded_file = st.file_uploader("Upload an Image...", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        # Display the uploaded image
        st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
        
        # Save the uploaded file temporarily
        with open(uploaded_file.name, "wb") as file:
            file.write(uploaded_file.getvalue())
        
        # Process the image
        with st.spinner("Analyzing the image..."):
            scenario = img2txt(uploaded_file.name)
        
        with st.spinner("Generating story..."):
            story = generate_story(scenario)
        
        # Display results
        with st.expander("Image Description"):
            st.write(scenario)
        
        with st.expander("Generated Story"):
            st.write(story)
        
        # Generate audio
        with st.spinner("Converting story to audio..."):
            if text_to_speech(story):
                st.success("Audio generated successfully!")
                try:
                    # Try to play the audio file
                    with open("audio.flac", "rb") as audio_file:
                        audio_bytes = audio_file.read()
                        st.audio(audio_bytes, format="audio/flac")
                except FileNotFoundError:
                    st.error("Audio file not found. There might be an issue with the text-to-speech service.")
            else:
                st.error("Failed to generate audio. Please try again.")
        
        # Clean up temporary files
        try:
            os.remove(uploaded_file.name)
            if os.path.exists("audio.flac"):
                os.remove("audio.flac")
        except:
            pass  # Ignore cleanup errors

if __name__ == '__main__':
    main()
