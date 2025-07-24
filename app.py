from dotenv import find_dotenv, load_dotenv
import requests
import os
import transformers
from transformers import pipeline
import streamlit as st

# Load environment variables
try:
    load_dotenv(find_dotenv())
    HUGGINGFACEHUB_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")
except Exception as e:
    st.error(f"Error loading environment: {e}")
    HUGGINGFACEHUB_API_TOKEN = None

def img2txt(image_path):
    try:
        pipe = pipeline("image-to-text", model="Salesforce/blip-image-captioning-base")
        text = pipe(image_path)[0]['generated_text']
        print(text)
        return text
    except Exception as e:
        st.error(f"Error in image captioning: {e}")
        return "a beautiful scene"

def generate_story(scenario):
    try:
        intro = "write a meaningfull story in about 300 words about "
        full_prompt = f"{intro} {scenario}"
        
        pipe = transformers.pipeline("text-generation", model="gpt2")
        output = pipe(full_prompt, num_return_sequences=1, max_length=300, truncation=True)
        generated_story = output[0]['generated_text']
        story = generated_story[len(intro):].strip()  
        
        return story
    except Exception as e:
        st.error(f"Error generating story: {e}")
        return f"Once upon a time, there was {scenario}. It was a wonderful moment filled with beauty and wonder."

def text_speech(message):
    try:
        if not HUGGINGFACEHUB_API_TOKEN:
            st.error("Hugging Face API token not found!")
            return False
            
        API_URL = "https://api-inference.huggingface.co/models/microsoft/speecht5_tts"
        headers = {"Authorization": f"Bearer {HUGGINGFACEHUB_API_TOKEN}"}
        payload = {"inputs": message}
        
        response = requests.post(API_URL, headers=headers, json=payload)
        
        if response.status_code == 200:
            with open('audio.flac', 'wb') as file:
                file.write(response.content)
            return True
        else:
            st.error(f"TTS API failed with status: {response.status_code}")
            return False
    except Exception as e:
        st.error(f"Error in text-to-speech: {e}")
        return False



def main():
    try:
        st.set_page_config(page_title="IMAGE TO AUDIO", page_icon="🎵")
        st.header("Turn Image into an Audio Story")

        uploaded_file = st.file_uploader("Upload an Image...", type=["jpg", "jpeg", "png"])

        if uploaded_file is not None:
            try:
                # Save uploaded file
                with open(uploaded_file.name, "wb") as file:
                    file.write(uploaded_file.getvalue())

                st.image(uploaded_file, caption="Uploaded Image..", use_container_width=True)

                with st.spinner("Analyzing image..."):
                    scenario = img2txt(uploaded_file.name)

                with st.spinner("Generating story..."):
                    story = generate_story(scenario)

                with st.spinner("Converting to audio..."):
                    audio_success = text_speech(story)

                if audio_success:
                    st.success("Audio generated successfully!")
                    st.audio("audio.flac")
                else:
                    st.warning("Audio generation failed, but you can still read the story below.")

                with st.expander("Image Description"):
                    st.write(scenario)

                with st.expander("Generated Story"):
                    st.write(story)

                # Clean up uploaded file
                try:
                    os.remove(uploaded_file.name)
                except:
                    pass

            except Exception as e:
                st.error(f"Error processing your image: {e}")
                st.info("Please try uploading a different image.")

    except Exception as e:
        st.error(f"Application error: {e}")
        st.info("Please refresh the page and try again.")

if __name__ == '__main__':
    main()
