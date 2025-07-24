# 🎿 Image-to-Audio Story Converter

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://genai-project-6b5bre75bfmupqpa8npwz5.streamlit.app)

🔗 **Live Demo**: [genai-project-6b5bre75bfmupqpa8npwz5.streamlit.app](https://genai-project-6b5bre75bfmupqpa8npwz5.streamlit.app)

This project converts images into engaging audio stories using image captioning, text generation, and browser-based speech synthesis.

---

## 📌 Overview

The app performs the following steps:

1. 🖼️ **Image-to-Text**: Captions images using `Salesforce/blip-image-captioning-base`.
2. 📜 **Text-to-Story**: Expands captions into stories using `GPT-2`.
3. 🔊 **Text-to-Speech**: Converts stories into audio using browser's built-in SpeechSynthesis API.

---

## 🧠 Technologies Used

* **Python**: Core backend processing
* **Streamlit**: Frontend UI framework
* **Hugging Face Transformers**: Access to GPT-2 and image models
* **Hugging Face Inference API**: For accessing models like BLIP and GPT-2
* **BLIP (Salesforce)**: Image captioning model
* **Browser SpeechSynthesis**: In-browser TTS using JavaScript (no external TTS API needed)

---

## 🚀 Setup & Usage

### 1. Clone the repository:

```bash
git clone https://github.com/fahad10inb/GenAI-Project.git
cd GenAI-Project
```

### 2. Install dependencies:

```bash
pip install -r requirements.txt
```

### 3. Run the app:

```bash
streamlit run app.py
```

### 4. Use the UI:

* Upload an image.
* View the AI-generated caption.
* Generate a story from the caption.
* Listen to the story using browser-based audio playback.

---

## 🔊 Text-to-Speech (Browser-based)

No need for external models or installations — audio is generated using the browser’s built-in SpeechSynthesis API.

> 💡 Works out of the box on Chrome, Edge, and Firefox with natural voices.

---

## 🌱 Future Enhancements

* Improve caption-to-story creativity with fine-tuned LLMs.
* Add multilingual support for narration.
* Allow custom voice selection and speech rate control.
* Optional export of audio to downloadable `.wav` using ESPnet locally.

---

## 👥 Contributors

* **GitHub**: [Fahad10inb](https://github.com/fahad10inb)
* **Email**: [fahadrahiman10@gmail.com](mailto:fahadrahiman10@gmail.com)

---
