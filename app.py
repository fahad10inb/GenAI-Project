from dotenv import find_dotenv, load_dotenv
import requests
import os
import transformers
from transformers import pipeline
import streamlit as st
load_dotenv(find_dotenv())
HUGGINGFACEHUB_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")

def img2txt(url):
    pipe = pipeline("image-to-text", model="Salesforce/blip-image-captioning-base")
    text = pipe(url)[0]['generated_text']
    print(text)
    return text


def generate_story(check):
    intro = "write a meaningfull story in about 300 words about "
    full_prompt = f"{intro} {check}"
    
    pipe = transformers.pipeline("text-generation", model="gpt2")
    output = pipe(full_prompt, num_return_sequences=1, max_length=300, truncation=True)
    generated_story = output[0]['generated_text']
    story = generated_story[len(intro):].strip()  
    
    return story


def text_speech(message):
    API_URL = "https://api-inference.huggingface.co/models/microsoft/speecht5_tts"
    headers = {"Authorization": f"Bearer {HUGGINGFACEHUB_API_TOKEN}"}
    payload = {"inputs": message}
    
    response = requests.post(API_URL, headers=headers, json=payload)
    
    if response.status_code == 200:
        with open('audio.flac', 'wb') as file:
            file.write(response.content)
        return True
    else:
        print(f"TTS API failed with status: {response.status_code}")
        return False



def main():
    st.set_page_config(page_title="IMAGE TO AUDIO", page_icon="")

    st.header("Turn Image into an Audio Story")

    uploaded_file = st.file_uploader("Upload an Image...", type="jpg")

    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()

        with open(uploaded_file.name, "wb") as file:
            file.write(bytes_data)

        st.image(uploaded_file, caption="Uploaded Image..", use_container_width=True)

        scenario = img2txt(uploaded_file.name)
        story = generate_story(scenario)

        if text_speech(story):
            st.audio("audio.flac")
        else:
            st.error("Audio generation failed. The story is displayed above.")

        with st.expander("Situation"):
            st.write(scenario)

        with st.expander("Story"):
            st.write(story)

if __name__ == '__main__':
    main()
