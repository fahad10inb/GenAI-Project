# 🎿 Image-to-Audio Story Converter

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://genai-project-6b5bre75bfmupqpa8npwz5.streamlit.app)

🔗 **Live Demo**: [genai-project-6b5bre75bfmupqpa8npwz5.streamlit.app](https://genai-project-6b5bre75bfmupqpa8npwz5.streamlit.app)

This project converts images into engaging audio stories using image captioning, text generation, and text-to-speech models.

---

## 📌 Overview

The app performs the following steps:

1. 🖼️ **Image-to-Text**: Captions images using `Salesforce/blip-image-captioning-base`.
2. 📜 **Text-to-Story**: Expands captions into stories using `GPT-2`.
3. 🔊 **Text-to-Speech**: Converts stories into audio using `ESPnet Kan-Bayashi LJSpeech VITS`.

---

## 🧠 Technologies Used

* **Python**: Core backend processing
* **Streamlit**: Frontend UI framework
* **Hugging Face Transformers**: Access to GPT-2 and image models
* **Hugging Face Inference API**: For text-to-speech model usage
* **BLIP (Salesforce)**: Image captioning model
* **ESPnet**: TTS model backend (`kan-bayashi_ljspeech_vits`)

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
* View the caption.
* Generate a story.
* Click to play the generated audio story.

---

## 🔊 ESPnet TTS Integration (Local Option)

If using ESPnet locally instead of Hugging Face API:

```bash
pip install espnet
```

```python
from espnet2.bin.tts_inference import Text2Speech

model = Text2Speech.from_pretrained("espnet/kan-bayashi_ljspeech_vits")
speech, *_ = model("Once upon a time...")

with open("output.wav", "wb") as f:
    f.write(speech.numpy())
```

---

## 🌱 Future Enhancements

* Improve caption-to-story creativity with fine-tuned LLMs.
* Add multilingual support for narration.
* Allow custom voice selection for audio playback.

---

## 👥 Contributors

* **GitHub**: [Fahad10inb](https://github.com/fahad10inb)
* **Email**: [fahadrahiman10@gmail.com](mailto:fahadrahiman10@gmail.com)

---
